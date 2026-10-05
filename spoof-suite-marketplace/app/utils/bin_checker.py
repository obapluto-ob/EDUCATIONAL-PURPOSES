import requests
import logging

# Set up logging
logger = logging.getLogger(__name__)

def check_bin(bin_number):
    """
    Real BIN checker using binlist.net API.

    Args:
        bin_number (str): The BIN number to check (first 6-8 digits of card)

    Returns:
        dict: BIN information or error message
    """
    # Validate input
    if not bin_number or not bin_number.isdigit():
        return {"error": "Invalid BIN number. Must be numeric."}

    if len(bin_number) < 6:
        return {"error": "BIN number must be at least 6 digits."}

    try:
        response = requests.get(
            f"https://lookup.binlist.net/{bin_number}",
            headers={"Accept-Version": "3"},
            timeout=10  # Add timeout
        )

        if response.status_code == 200:
            data = response.json()
            bin_info = {
                "bin": bin_number,
                "type": data.get("type", "Unknown").title(),
                "brand": data.get("scheme", "Unknown").title(),
                "level": data.get("brand", "Unknown").title(),
                "prepaid": "Yes" if data.get("prepaid") else "No",
                "bank": data.get("bank", {}).get("name", "Unknown") if data.get("bank") else "Unknown",
                "country": f'{data.get("country", {}).get("name", "Unknown")} {data.get("country", {}).get("emoji", "")}' if data.get("country") else "Unknown"
            }
            logger.info(f"Successfully checked BIN: {bin_number}")
        elif response.status_code == 404:
            bin_info = {"error": "BIN not found in database."}
        elif response.status_code == 429:
            bin_info = {"error": "Rate limit exceeded. Please try again later."}
        else:
            bin_info = {"error": f"API error: {response.status_code}"}

    except requests.exceptions.Timeout:
        bin_info = {"error": "Request timeout. Please try again."}
        logger.error(f"Timeout checking BIN: {bin_number}")
    except requests.exceptions.ConnectionError:
        bin_info = {"error": "Connection error. Please check your internet connection."}
        logger.error(f"Connection error checking BIN: {bin_number}")
    except requests.exceptions.RequestException as e:
        bin_info = {"error": f"Request error: {str(e)}"}
        logger.error(f"Request error checking BIN {bin_number}: {str(e)}")
    except Exception as e:
        bin_info = {"error": "An unexpected error occurred."}
        logger.error(f"Unexpected error checking BIN {bin_number}: {str(e)}")

    return bin_info