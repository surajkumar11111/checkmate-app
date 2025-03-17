import streamlit as st
from dotenv import load_dotenv
from PIL import Image
from pdf2image import convert_from_bytes
import io
from apiconfig import extract_cheque_details
from dbconnection import insert_cheque_details, init_db_connection

load_dotenv()

# initialize DB connection once
init_db_connection()

# custom CSS
st.markdown(
    """
    <style>
        .stFileUploader { width: 80% !important; }
        .custom-success {
            width: 80% !important;
            background-color: #d4edda !important;
            color: #155724 !important;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
            font-weight: bold;
            margin-top: 10px;
        }
        .stFileUploader label div { display: none !important; }
        .stButton > button {
            background-color: #0cc789 !important;
            color: white !important;
            border-radius: 7px !important;
            border: none !important;
            font-size: 16px !important;
            padding: 6px 15px !important;
            cursor: pointer;
        }
        .stButton > button:hover { background-color: #a0d1c1 !important; }
    </style>
    """,
    unsafe_allow_html=True
)

st.subheader("Upload Cheque Image or PDF")

# initialize session state
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "cheque_details" not in st.session_state:
    st.session_state.cheque_details = None

def process_uploaded_file(uploaded_file):
    """ Process uploaded file: Convert images & PDFs to byte arrays. """
    if uploaded_file.type.startswith("image/"):
        # convert single cheque image
        image = Image.open(uploaded_file).convert("RGB")
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="JPEG")
        return [{"mime_type": uploaded_file.type, "data": img_byte_arr.getvalue()}]

    elif uploaded_file.type == "application/pdf":
        # convert PDF pages to images
        images = convert_from_bytes(uploaded_file.getvalue())
        if not images:
            raise ValueError("Failed to convert PDF to images.")

        return [{"mime_type": "image/jpeg", "data": io.BytesIO(img.convert("RGB").tobytes()).getvalue()} for img in images]

    else:
        raise ValueError("Unsupported file type.")

# file uploader
upload_file = st.file_uploader("Upload a Cheque Image or PDF", type=["jpg", "jpeg", "png", "pdf"], label_visibility="collapsed")

if upload_file is not None:
    st.session_state.uploaded_file = upload_file

# process Button
if st.button("Process") and st.session_state.uploaded_file is not None:
    with st.spinner("Processing... Please wait ⏳"):
        try:
            # avoid reprocessing the same file
            if "last_uploaded_file" in st.session_state and st.session_state.last_uploaded_file == hash(st.session_state.uploaded_file.getvalue()):
                st.warning("This file has already been processed.")
                st.stop()

            # store file hash in session state to prevent reprocessing
            st.session_state.last_uploaded_file = hash(st.session_state.uploaded_file.getvalue())

            file_contents = process_uploaded_file(st.session_state.uploaded_file)

            if not file_contents:
                st.error("No valid cheque images found in the file.")
                st.stop()

            cheque_details_list = []

            for idx, file_content in enumerate(file_contents):
                response_data = extract_cheque_details(file_content["data"])  # extract details

                if response_data is None:
                    st.error(f"Page {idx + 1}: API returned no response.")
                    continue  # skip to next page

                if not isinstance(response_data, dict):
                    raise ValueError(f"Page {idx + 1}: API response is invalid.")

                cheque_details_list.append(response_data)  # store cheque data

            # store extracted details in session state
            st.session_state.cheque_details = cheque_details_list

            # insert into Supabase DB
            for cheque_data in cheque_details_list:
                insert_cheque_details(cheque_data)

            st.success("Cheque details processed successfully! Check the dashboard.")
        
        except Exception as e:
            st.error(f"Error: {e}")
