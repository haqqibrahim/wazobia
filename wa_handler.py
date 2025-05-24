import os
from dotenv import load_dotenv
import requests
import json
from pydub import AudioSegment

load_dotenv()

PHONE_NUMBER_ID = os.environ.get("WA_PHONE_NUMBER_ID")
ACCESS_TOKEN = os.getenv("WA_ACCESS_TOKEN")
api_version = "v18.0"

messaging_url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
messaging_headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {ACCESS_TOKEN}",
}


async def send_message(message: str, phone_number: str):
    payload = json.dumps(
        {
            "messaging_product": "whatsapp",
            "to": str(phone_number),
            "type": "text",
            "text": {"preview_url": False, "body": message},
        }
    )

    requests.request("POST", messaging_url, headers=messaging_headers, data=payload)
    print("MESSAGE SENT")

async def get_whatsapp_media(audio_media_id: str) -> bytes:
    # Step 1: Get the media URL using the media ID
    media_info_url = f"https://graph.facebook.com/{api_version}/{audio_media_id}?phone_number_id={PHONE_NUMBER_ID}"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    response = requests.get(media_info_url, headers=headers)
    response.raise_for_status()
    media_url = response.json()["url"]
    
    # Step 2: Download the audio file from the media URL
    media_response = requests.get(media_url, headers=headers)
    media_response.raise_for_status()
    
    return media_response.content

async def upload_audio_file(file_path: str) -> str:
    """
    Uploads an audio file to WhatsApp and returns the media ID.
    Args:
        file_path: Path to the MP3 audio file
    Returns:
        str: The media ID of the uploaded file
    """
    url = f"https://graph.facebook.com/{api_version}/{PHONE_NUMBER_ID}/media"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }

    # Verify file exists and is an MP3
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found at {file_path}")
    
    # If the file is a .wav, convert it to .mp3 and update file_path
    if file_path.lower().endswith(".wav"):
        audio = AudioSegment.from_wav(file_path)
        mp3_file_path = file_path.replace(".wav", ".mp3")
        audio.export(mp3_file_path, format="mp3")
        file_path = mp3_file_path
        
    
    
    with open(file_path, "rb") as audio_file:
        files = {
            'messaging_product': (None, 'whatsapp'),
            'file': (os.path.basename(file_path), audio_file, 'audio/mpeg')
        }
        
        try:
            response = requests.post(url, headers=headers, files=files)
            
            if response.status_code != 200:
                print(f"Error Response: {response.text}")
                response.raise_for_status()
                
            media_id = response.json().get("id")
            if not media_id:
                raise Exception("Failed to upload audio file: No media ID returned")
                
            return media_id
            
        except requests.exceptions.RequestException as e:
            print(f"Upload failed: {str(e)}")
            raise

async def send_voice_message(file_path: str, phone_number: str):
    """
    Sends a voice message to a WhatsApp number and verifies delivery.
    Args:
        file_path: Path to the MP3 audio file
        phone_number: The recipient's phone number
    """
    try:
        # Upload the audio file
        audio_media_id = await upload_audio_file(file_path)
        print(f"Audio Media ID: {audio_media_id}")
        print(f"Phone Number: {phone_number}")
        
        payload = json.dumps({
            "messaging_product": "whatsapp",
            "to": str(phone_number),
            "type": "audio",
            "audio": {"id": audio_media_id}
        })

        # Send the message and get the response
        response = requests.post(messaging_url, headers=messaging_headers, data=payload)
        response.raise_for_status()
        
        # Check the response content
        response_data = response.json()
        if 'messages' not in response_data or not response_data['messages']:
            raise Exception("No message ID returned in response")
            
        message_id = response_data['messages'][0]['id']
        print(f"Message sent successfully. Message ID: {message_id}")
        
    except requests.exceptions.RequestException as e:
        print(f"Failed to send voice message: {str(e)}")
        print(f"Response content: {e.response.text if hasattr(e, 'response') else 'No response'}")
        raise
    except Exception as e:
        print(f"Error sending voice message: {str(e)}")
        raise