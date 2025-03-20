import io
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
import logging

load_dotenv()

# configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is missing in environment variables.")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")


PROMPT = PROMPT = """Extract details from the scanned cheque and return the response in JSON format:
    {
        "payee_name": "Full name of the payee",
        "cheque_date": "yyyy-mm-dd (e.g., '2025-02-20')",
        "cheque_number": "Cheque number as it appears",
        "account_number": "Numeric only, ignore any characters",
        "bank_name": "Full name of the bank",
        "amount": "Numeric form only (e.g., '20000')"
    }
        Ensure correct JSON formatting, return empty strings for missing fields, and strictly use 'YYYY-MM-DD' for cheque_date.        
    """

def extract_cheque_details(image_bytes):
    """Extract cheque details using Gemini API and return a structured JSON response."""
    try:
        # open image from bytes
        opened_image = Image.open(io.BytesIO(image_bytes))

        # generate response from Gemini API
        response = model.generate_content([PROMPT, opened_image])

        # ensure response text exists
        if not hasattr(response, "text") or not response.text.strip():
            raise ValueError("API returned no valid response.")

        response_text = response.text.strip().replace("```json", "").replace("```", "")

        # validate JSON response
        try:
            response_dict = json.loads(response_text)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON response: {response_text}")
            raise ValueError(f"Failed to parse JSON response: {e}")

        # ensure required fields exist
        required_keys = ["payee_name", "cheque_date", "cheque_number", "account_number", "bank_name", "amount"]
        for key in required_keys:
            response_dict.setdefault(key, "")

        # validate date format
        if response_dict["cheque_date"]:
            try:
                from datetime import datetime
                response_dict["cheque_date"] = datetime.strptime(response_dict["cheque_date"], "%Y-%m-%d").strftime("%Y-%m-%d")
            except ValueError:
                logging.warning(f"Invalid cheque_date format: {response_dict['cheque_date']}")
                response_dict["cheque_date"] = ""

        return response_dict

    except Exception as e:
        logging.error(f"Error processing image: {e}")
        return None  