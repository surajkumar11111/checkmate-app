import psycopg2
import streamlit as st
import os
import logging
from dotenv import load_dotenv


load_dotenv()

# set up logging
logging.basicConfig(level=logging.INFO)

def init_db_connection():
    """Initialize a single database connection using Streamlit session state."""
    try:
        if "db_connection" not in st.session_state or st.session_state.db_connection is None:
            st.session_state.db_connection = psycopg2.connect(
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT")
            )
            logging.info("Connected to Supabase PostgreSQL successfully.")
    except Exception as err:
        logging.error(f"Database connection failed: {err}")
        st.session_state.db_connection = None  # ensure no invalid conn is stored

def get_db_connection():
    """Retrieve the existing database connection from session state."""
    if "db_connection" not in st.session_state or st.session_state.db_connection is None:
        init_db_connection()
    return st.session_state.db_connection

def insert_cheque_details(details):
    """Insert cheque details into Supabase PostgreSQL."""
    insert_query = """
        INSERT INTO cheque_details_tbl (
            cheque_date, account_number, bank_name, cheque_number, 
            payee_name, amount, status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    try:
        connection = get_db_connection()
        if connection is None:
            raise ConnectionError("Database connection is unavailable.")

        with connection.cursor() as cursor:
            cursor.execute(insert_query, (
                details.get("cheque_date", ""),
                details.get("account_number", ""),
                details.get("bank_name", ""),
                details.get("cheque_number", ""),
                details.get("payee_name", ""),
                details.get("amount", ""),
                details.get("status", "Processed")
            ))
            connection.commit()
            logging.info("Cheque details inserted successfully.")
    except Exception as err:
        logging.error(f"Error inserting cheque details: {err}")
        raise

def fetch_cheque_details():
    """Fetch all cheque details from Supabase."""
    try:
        connection = get_db_connection()
        if connection is None:
            raise ConnectionError("Database connection is unavailable.")

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT cheque_date, account_number, bank_name, cheque_number, 
                       payee_name, amount, uploaded_at, status
                FROM cheque_details_tbl
            """)
            return cursor.fetchall()
    except Exception as err:
        logging.error(f"Error fetching cheque details: {err}")
        return []