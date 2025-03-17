import streamlit as st
import pandas as pd
from dbconnection import fetch_cheque_details, init_db_connection
import io
from fpdf import FPDF
from docx import Document
from streamlit_lottie import st_lottie # type: ignore
import json

init_db_connection()

if "cheque_data" not in st.session_state:
    st.session_state.cheque_data = pd.DataFrame()

# fetch cheque data & store in session state
if st.session_state.cheque_data.empty:
    records = fetch_cheque_details()
    if records:
        expected_columns = ["cheque_date", "account_number", "bank_name", "cheque_number", "payee_name", "amount", "uploaded_at"]
        if len(records[0]) == 8:
            expected_columns.append("status")
        st.session_state.cheque_data = pd.DataFrame(records, columns=expected_columns)

# load data from session state
df = st.session_state.cheque_data

st.subheader("Export Cheque Records")

st.markdown("""
    <style>
        div[data-testid="column"] {
            padding: 0px !important;
        }
    </style>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    def load_lottiefile(filepath: str):
        with open(filepath, "r") as f:
            return json.load(f)

    first_anim_lottie = load_lottiefile("images/Animation-Exports.json")
    st_lottie(
        first_anim_lottie,
        speed=1,
        loop=True,
        quality="low",
        width=510,
        key="three"
    )

with col2:
    st.markdown("""
    <style>
        div[data-testid="column"] { padding: 0px !important; }
        .stDownloadButton { margin-top: 15px !important; }
        .stDownloadButton button {
            width: 90% !important;
            height: 60px !important;
            background-color: #0cc789 !important;
            color: white !important;
            border-radius: 5px !important;
            border: none !important;
            font-size: 16px !important;
            margin-bottom: 8px;
        }
        .stDownloadButton button:hover { background-color: #a0d1c1 !important; }
    </style>
    """, unsafe_allow_html=True)

    if df is not None and not df.empty:
        def convert_df_to_csv(dataframe):
            """Convert DataFrame to CSV"""
            return dataframe.to_csv(index=False).encode('utf-8')
        
        csv_data = convert_df_to_csv(df)
        st.download_button("Download as CSV", data=csv_data, file_name="cheque_records.csv", mime="text/csv")

        def convert_df_to_pdf(dataframe):
            """Convert DataFrame to PDF"""
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            for col in dataframe.columns:
                pdf.cell(40, 10, col, border=1)
            pdf.ln()

            for _, row in dataframe.iterrows():
                for item in row:
                    pdf.cell(40, 10, str(item), border=1)
                pdf.ln()

            output = io.BytesIO()
            pdf_data = pdf.output(dest="S").encode("latin1")
            output.write(pdf_data)
            output.seek(0)
            return output
        
        pdf_data = convert_df_to_pdf(df)
        st.download_button("Download as PDF", data=pdf_data, file_name="cheque_records.pdf", mime="application/pdf")

        def convert_df_to_excel(dataframe):
            """Convert DataFrame to Excel"""
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                dataframe.to_excel(writer, index=False, sheet_name="Cheque Records")
            output.seek(0)
            return output
        
        excel_data = convert_df_to_excel(df)
        st.download_button("Download as Excel", data=excel_data, file_name="cheque_records.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        def convert_df_to_docx(dataframe):
            """Convert DataFrame to DOCX"""
            doc = Document()
            doc.add_heading("Cheque Records", level=1)

            table = doc.add_table(rows=1, cols=len(dataframe.columns))
            hdr_cells = table.rows[0].cells
            for i, col_name in enumerate(dataframe.columns):
                hdr_cells[i].text = col_name

            for _, row in dataframe.iterrows():
                row_cells = table.add_row().cells
                for i, item in enumerate(row):
                    row_cells[i].text = str(item)

            output = io.BytesIO()
            doc.save(output)
            output.seek(0)
            return output
        
        docx_data = convert_df_to_docx(df)
        st.download_button("Download as DOCX", data=docx_data, file_name="cheque_records.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    else:        
        st.warning("No cheque records available for export.")
