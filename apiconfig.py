import io
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
import streamlit as st

# load environment variables
load_dotenv()

# configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("API Key is missing.")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")


PROMPT = """Extract details from the scanned cheque and return the response in JSON format:
{
    "payee_name": "Full name of the payee",
    "cheque_date": "dd-mm-yyyy (e.g., '20-02-2025')",
    "cheque_number": "Cheque number as it appears",
    "account_number": "Numeric only, ignore any characters",
    "bank_name": "Full name of the bank",
    "amount": "Numeric form only (e.g., '20000')"
}
Ensure correct JSON formatting, return empty strings for missing fields.
"""

def extract_cheque_details(image_bytes):
    """Extract cheque details using Gemini API and return a structured JSON response."""

    # if image already processed in session state
    image_hash = hash(image_bytes)
    if "cheque_details" in st.session_state and st.session_state.cheque_details.get("image_hash") == image_hash:
        return st.session_state.cheque_details["data"]

    try:
        # open image from bytes
        opened_image = Image.open(io.BytesIO(image_bytes))

        # generate response from Gemini API
        response = model.generate_content([PROMPT, opened_image])

        if hasattr(response, "text"):
            response_text = response.text.strip().replace("```json", "").replace("```", "")
            
            # parse JSON response
            response_dict = json.loads(response_text)

            # validate JSON structure
            required_keys = ["payee_name", "cheque_date", "cheque_number", "account_number", "bank_name", "amount"]
            for key in required_keys:
                if key not in response_dict:
                    response_dict[key] = ""  # ensure all required keys exist

            # store response in session state
            st.session_state.cheque_details = {
                "image_hash": image_hash,
                "data": response_dict
            }

            return response_dict
        else:
            raise ValueError("API returned no response.")

    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON response: {e}")
    except Exception as e:
        raise ValueError(f"Error processing image: {e}")
