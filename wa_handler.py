import os
import json
import requests
from dotenv import load_dotenv
from pydub import AudioSegment

# Load environment variables from .env file
load_dotenv()

# WhatsApp API configuration
PHONE_NUMBER_ID = os.environ.get("WA_PHONE_NUMBER_ID")
ACCESS_TOKEN = os.getenv("WA_ACCESS_TOKEN")
API_VERSION = "v18.0"

MESSAGING_URL = f"https://graph.facebook.com/{API_VERSION}/{PHONE_NUMBER_ID}/messages"
MESSAGING_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {ACCESS_TOKEN}",
}


async def send_message(message: str, phone_number: str) -> None:
    """
    Sends a text message to a WhatsApp number.

    Args:
        message (str): The message body to send.
        phone_number (str): The recipient's phone number.
    """
    payload = json.dumps({
        "messaging_product": "whatsapp",
        "to": str(phone_number),
        "type": "text",
        "text": {"preview_url": False, "body": message},
    })

    try:
        response = requests.post(MESSAGING_URL, headers=MESSAGING_HEADERS, data=payload)
        response.raise_for_status()
        print("MESSAGE SENT")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send message: {e}")
        raise


async def get_whatsapp_media(audio_media_id: str) -> bytes:
    """
    Downloads a media file from WhatsApp using its media ID.

    Args:
        audio_media_id (str): The media ID of the audio file.

    Returns:
        bytes: The content of the downloaded media file.
    """
    # Step 1: Get the media URL using the media ID
    media_info_url = (
        f"https://graph.facebook.com/{API_VERSION}/{audio_media_id}"
        f"?phone_number_id={PHONE_NUMBER_ID}"
    )
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    try:
        response = requests.get(media_info_url, headers=headers)
        response.raise_for_status()
        media_url = response.json().get("url")
        if not media_url:
            raise Exception("Media URL not found in response.")

        # Step 2: Download the audio file from the media URL
        media_response = requests.get(media_url, headers=headers)
        media_response.raise_for_status()
        return media_response.content
    except requests.exceptions.RequestException as e:
        print(f"Failed to download media: {e}")
        raise


async def upload_audio_file(file_path: str) -> str:
    """
    Uploads an audio file to WhatsApp and returns the media ID.

    Args:
        file_path (str): Path to the audio file (MP3 or WAV).

    Returns:
        str: The media ID of the uploaded file.
    """
    url = f"https://graph.facebook.com/{API_VERSION}/{PHONE_NUMBER_ID}/media"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }

    # Verify file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found at {file_path}")

    # Convert WAV to MP3 if necessary
    if file_path.lower().endswith(".wav"):
        try:
            audio = AudioSegment.from_wav(file_path)
            mp3_file_path = file_path.rsplit(".", 1)[0] + ".mp3"
            audio.export(mp3_file_path, format="mp3")
            file_path = mp3_file_path
        except Exception as e:
            print(f"Failed to convert WAV to MP3: {e}")
            raise

    # Open the file safely and upload
    try:
        with open(file_path, "rb") as audio_file:
            files = {
                'messaging_product': (None, 'whatsapp'),
                'file': (os.path.basename(file_path), audio_file, 'audio/mpeg')
            }
            response = requests.post(url, headers=headers, files=files)
            if response.status_code != 200:
                print(f"Error Response: {response.text}")
                response.raise_for_status()

            media_id = response.json().get("id")
            if not media_id:
                raise Exception("Failed to upload audio file: No media ID returned")
            return media_id
    except requests.exceptions.RequestException as e:
        print(f"Upload failed: {e}")
        raise
    except Exception as e:
        print(f"Error handling audio file: {e}")
        raise


async def send_voice_message(file_path: str, phone_number: str) -> None:
    """
    Sends a voice message (audio file) to a WhatsApp number.

    Args:
        file_path (str): Path to the audio file (MP3 or WAV).
        phone_number (str): The recipient's phone number.
    """
    try:
        # Upload the audio file and get the media ID
        audio_media_id = await upload_audio_file(file_path)
        print(f"Audio Media ID: {audio_media_id}")
        print(f"Phone Number: {phone_number}")

        payload = json.dumps({
            "messaging_product": "whatsapp",
            "to": str(phone_number),
            "type": "audio",
            "audio": {"id": audio_media_id}
        })

        # Send the audio message
        response = requests.post(MESSAGING_URL, headers=MESSAGING_HEADERS, data=payload)
        response.raise_for_status()

        # Check the response for message ID
        response_data = response.json()
        if 'messages' not in response_data or not response_data['messages']:
            raise Exception("No message ID returned in response")

        message_id = response_data['messages'][0]['id']
        print(f"Message sent successfully. Message ID: {message_id}")

    except requests.exceptions.RequestException as e:
        print(f"Failed to send voice message: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response content: {e.response.text}")
        raise
    except Exception as e:
        print(f"Error sending voice message: {e}")
        raise