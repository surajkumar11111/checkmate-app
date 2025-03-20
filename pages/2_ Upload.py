import streamlit as st
from dotenv import load_dotenv
from PIL import Image
from pdf2image import convert_from_bytes
import io
from apiconfig import extract_cheque_details  
from dbconnection import insert_cheque_details, init_db_connection

# load environment variables
load_dotenv()

# initialize DB connection
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
            color: black !important;
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

import subprocess
def check_poppler_path():
    result = subprocess.run(["which", "pdftoppm"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    poppler_path = result.stdout.strip()
    if poppler_path:
        print(f"Poppler is installed at: {poppler_path}")
    else:
        print("Poppler is NOT found in PATH.")
    return poppler_path

POPPLER_PATH = check_poppler_path()


def process_uploaded_file(uploaded_file):
    """Process uploaded cheque image or multi-page PDF."""
    if uploaded_file is not None:
        if uploaded_file.type.startswith("image/"):
            # convert single cheque image
            image = Image.open(uploaded_file).convert("RGB")
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format="JPEG")
            return [{"mime_type": uploaded_file.type, "data": img_byte_arr.getvalue()}]

        elif uploaded_file.type == "application/pdf":
            # convert PDF pages to images
            images = convert_from_bytes(uploaded_file.getvalue(), fmt="jpeg")
            if not images:
                raise ValueError("Failed to convert PDF to images.")

            processed_images = []
            for img in images:
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format="JPEG")
                processed_images.append({"mime_type": "image/jpeg", "data": img_byte_arr.getvalue()})

            return processed_images  # return list of processed pages

        else:
            raise ValueError("Unsupported file type. Please upload JPG, PNG, or PDF.")

    else:
        raise FileNotFoundError("No file uploaded!")

# file uploader
upload_file = st.file_uploader("Upload a Cheque Image or PDF", type=["jpg", "jpeg", "png", "pdf"], label_visibility="collapsed")

# process button
if st.button("Process") and upload_file is not None:
    with st.spinner("Processing... Please wait ⏳"):
        try:
            # prevent duplicate processing using file hash
            file_hash = hash(upload_file.getvalue())
            if "last_uploaded_file" in st.session_state and st.session_state.last_uploaded_file == file_hash:
                st.warning("This file has already been processed.")
                st.stop()

            st.session_state.last_uploaded_file = file_hash  # store hash

            file_contents = process_uploaded_file(upload_file)  # convert PDF/image to bytes

            if not file_contents:
                st.error("No valid cheque images found in the file.")
                st.stop()

            # process each page/image separately
            for idx, file_content in enumerate(file_contents):
                response_data = extract_cheque_details(file_content["data"])  # Call Gemini API

                # ensure response is valid
                if not isinstance(response_data, dict) or not response_data:
                    st.error(f"Page {idx}: API response is invalid or empty.")
                    continue  # skip to next page
                insert_cheque_details(response_data)

                st.markdown(
                    f'<div class="custom-success">Page {idx+1}: Cheque details processed successfully! Check the dashboard for details.</div>',
                    unsafe_allow_html=True
                )

        except Exception as e:
            st.error(f"Error: {e}")
