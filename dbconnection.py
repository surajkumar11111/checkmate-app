import logging
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# load environment variables
load_dotenv()

# set up logging
logging.basicConfig(level=logging.INFO)

# supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# initialize Supabase client
supabase: Client = None

def init_db_connection():
    """Initialize Supabase connection."""
    global supabase
    if supabase is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("Missing Supabase URL or API Key in environment variables.")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logging.info("Connected to Supabase successfully.")

# insert cheque details into Supabase
def insert_cheque_details(details):
    """Insert cheque details into Supabase."""
    try:
        init_db_connection()

        if not details or not isinstance(details, dict):
            logging.error("Invalid cheque details. Skipping insert.")
            return

        data = {
            "cheque_date": details.get("cheque_date", ""),
            "account_number": details.get("account_number", ""),
            "bank_name": details.get("bank_name", ""),
            "cheque_number": details.get("cheque_number", ""),
            "payee_name": details.get("payee_name", ""),
            "amount": details.get("amount", ""),
            "status": details.get("status", "Processed"),
        }
        response = supabase.table("cheque_details_tbl").insert(data).execute()

        if response.data:
            logging.info("Cheque details inserted successfully.")
        else:
            logging.error(f"Failed to insert cheque details: {response.error}")

    except Exception as err:
        logging.error(f"Error inserting cheque details: {err}")
        raise

# fetch cheque details from Supabase
def fetch_cheque_details():
    """Fetch all cheque details from Supabase."""
    try:
        init_db_connection()
        response = supabase.table("cheque_details_tbl").select("*").execute()
        
        if response.data:
            return response.data
        return []
    except Exception as err:
        logging.error(f"Error fetching cheque details: {err}")
        return []
    