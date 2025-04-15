## Project Title & Description
CheckMate - Automated Bank Check Processor

## Prerequisites
    Python 3.8+
    pip package manager

🚀 Overview

    CheckMate is a Streamlit-based web application that automates cheque data extraction from images and PDFs using the Gemini API. 
    Extracted details are stored in a Supabase PostgreSQL database, and users can view, analyze, and export the cheque records.

##  📌 Features

    - Automated Cheque Processing: Extract cheque details like date, amount, payee name, bank name, and cheque number.
    - Multi-File Support: Process multiple cheque images or PDFs in a single upload.
    - Dynamic Dashboard: Displays extracted cheque records with interactive visualization.
    - Export Options: Download cheque records in CSV, PDF, Excel, and DOCX formats.
    - Database Integration: Uses Supabase PostgreSQL for secure cheque data storage.
    - Responsive UI: Optimized for both desktop and mobile (with some limitations due to Streamlit)..


## 🔄 Technologies Used

    - Streamlit for UI, Custom CSS & Custom HTML
    - Gemini API for cheque detail extraction
    - Supabase PostgreSQL for database storage
    - FPDF, Pandas, Docx for exporting data    

## 🔗 Live Demo  
Check out the deployed application here:  
[🚀 CheckMate Live on Streamlit](https://checkmate-python-app.streamlit.app)


## How It Works

    I.  Upload Cheque Images/PDFs:
        Go to the Upload Page.
        Select and upload one or multiple cheque images or PDFs.
        The app processes and extracts details using the Gemini API.

    II. View Extracted Data:
        Navigate to the Dashboard Page.
        View cheque details like Cheque Number, Date, Payee, Amount, and Bank Name.
        The interactive table displays all extracted information from uploaded cheques.

    III.Export Processed Data:
        Visit the Exports Page.
        Download extracted cheque records in CSV, Excel, PDF, or DOCX formats.
