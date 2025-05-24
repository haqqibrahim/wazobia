import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import PlainTextResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db, Settings
import redis

from wa_handler import send_message, get_whatsapp_media, send_voice_message
from fastapi import status
from models import Translator

app = FastAPI()
# Add static files mounting
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure templates
templates = Jinja2Templates(directory="templates")

load_dotenv()

VERIFY_TOKEN = os.environ.get("WA_VERIFY_TOKEN")
PHONE_NUMBER_ID = os.environ.get("WA_PHONE_NUMBER_ID")
ACCESS_TOKEN = os.environ.get("WA_ACCESS_TOKEN")
REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = os.environ.get("REDIS_PORT")
REDIS_DECODE_RESPONSE = os.environ.get("REDIS_DECODE_RESPONSE")
REDIS_USERNAME = os.environ.get("REDIS_USERNAME")
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")
REDIS_PORT = os.environ.get("REDIS_PORT")

r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=REDIS_DECODE_RESPONSE,
    username=REDIS_USERNAME,
    password=REDIS_PASSWORD,
)

translator = Translator()


# Add this after your imports
async def get_user_settings(phone_number: str, db: Session) -> Settings:
    """
    Helper function to get user settings from database
    Returns None if user not found
    """
    settings = db.query(Settings).filter(Settings.phone_number == phone_number).first()
    return settings


@app.get("/")
async def root():
    return {"message": "Welcome to Wazobia"}

@app.get("/signup/form", response_class=HTMLResponse)
async def signup_form(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.get("/settings/form", response_class=HTMLResponse)
async def settings_form(request: Request):
    return templates.TemplateResponse("settings.html", {"request": request})


@app.post("/signup")
async def signup(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    required_fields = [
        "first_name",
        "last_name",
        "phone_number",
        "default_language",
        "output_language",
        "output_format",
    ]

    for field in required_fields:
        if field not in data:
            return {"error": f"Missing field: {field}", "status": "error"}
        
    # Convert nunber to use 234
    if data["phone_number"].startswith("0"):
        data["phone_number"] = "234" + data["phone_number"][1:]
    
    # Create new settings object
    settings = Settings(
        first_name=data["first_name"],
        last_name=data["last_name"],
        phone_number=data["phone_number"],
        default_language=data["default_language"],
        output_language=data["output_language"],
        output_format=data["output_format"],
    )

    # Add to database
    db.add(settings)
    db.commit()
    db.refresh(settings)

    return {"message": "User created successfully", "status": "success"}

@app.post("/settings")
async def update_setting(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    required_fields = [
        "phone_number",
        "default_language",
        "output_language",
        "output_format",
    ]

    for field in required_fields:
        if field not in data:
            return {"error": f"Missing field: {field}", "status": "error"}
    
    # Convert nunber to use 234
    if data["phone_number"].startswith("0"):
        data["phone_number"] = "234" + data["phone_number"][1:]
    
    # Update settings object
    settings = db.query(Settings).filter(Settings.phone_number == data["phone_number"]).first()
    if not settings:
        return {"error": "Settings not found for this phone number"}

    settings.default_language = data["default_language"]
    settings.output_language = data["output_language"]
    settings.output_format = data["output_format"]

    # Commit changes to database
    db.commit()
    db.refresh(settings)

    return {"message": "Settings updated successfully", "status": "success"}


  

@app.post("/send_message")
async def send_message_endpoint(request: Request):
    try:
        # Parse the incoming JSON payload
        body = await request.json()
        user_phone_number = body["user_phone_number"]
        message = body["message"]

        # Send the message using the send_message function
        await send_message(message, user_phone_number)

        return PlainTextResponse("Message sent successfully", status_code=200)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/webhook")
async def webhook_get(request: Request):
    hub_mode = request.query_params.get("hub.mode")
    hub_verify_token = request.query_params.get("hub.verify_token")
    hub_challenge = request.query_params.get("hub.challenge")

    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge, status_code=status.HTTP_200_OK)
    return PlainTextResponse("Forbidden", status_code=status.HTTP_403_FORBIDDEN)


@app.post("/webhook")
async def webhook_post(request: Request, db: Session = Depends(get_db)):
    try:
        body = await request.json()
        print(f"Received body: {body}")
        entry = body.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        contacts = value.get("contacts", [{}])
        messages = value.get("messages", [{}])

        # Deduplication
        message_obj = messages[0] if messages else {}
        message_id = message_obj.get("id")
        if message_id:
            redis_key = f"msgid:{message_id}"
            if r.get(redis_key):
                return PlainTextResponse(
                    "Message already processed", status_code=status.HTTP_200_OK
                )
            r.setex(redis_key, 600, 1)  # 10 minutes

        # Get user phone number
        user_phone_number = contacts[0].get("wa_id") if contacts else None
        if not user_phone_number:
            return PlainTextResponse("PROCESSED", status_code=status.HTTP_200_OK)

        # Handle text messages
        if messages and messages[0].get("text"):
            user_message = messages[0]["text"]["body"]
            user = await get_user_settings(phone_number=user_phone_number, db=db)
            if user:
                if user.output_format == "text":
                    text_response = await translator.text_to_text_translator(
                        user_message,
                        source=user.default_language,
                        target=user.output_language,
                    )
                    await send_message(
                        message=text_response, phone_number=user_phone_number
                    )
                elif user.output_format == "audio":
                    status_audio = await translator.text_to_voice_translator(
                        user_message, language=user.output_language
                    )
                    if status_audio:
                        await send_voice_message("new.wav", user_phone_number)
                    else:
                        await send_message(
                            message="Error processing audio file",
                            phone_number=user_phone_number,
                        )
                else:
                    text_response = await translator.text_to_text_translator(
                        user_message,
                        source=user.default_language,
                        target=user.output_language,
                    )
                    status_audio = await translator.text_to_voice_translator(
                        user_message, language=user.output_language
                    )
                    await send_message(
                        message=text_response, phone_number=user_phone_number
                    )
                    if status_audio:
                        await send_voice_message("new.wav", user_phone_number)
                    else:
                        await send_message(
                            message="Error processing audio file",
                            phone_number=user_phone_number,
                        )
            else:
                signup_link = "https://signup"
                msg = (
                    f"Welcome to Wazobia, your AI translator right here on WhatsApp, "
                    f"please click the link to signup \n{signup_link}"
                )
                await send_message(message=msg, phone_number=user_phone_number)

        # Handle audio messages
        elif messages and messages[0].get("audio"):
            audio_id = messages[0]["audio"].get("id")
            if audio_id:
                audio_bytes = await get_whatsapp_media(audio_media_id=audio_id)
                audio_file = f"{user_phone_number}.ogg"
                with open(audio_file, "wb") as f:
                    f.write(audio_bytes)

                user = await get_user_settings(phone_number=user_phone_number, db=db)
                if user:
                    if user.output_format == "text":
                        text_response = await translator.voice_to_text_translator(
                            file=audio_file, language=user.default_language
                        )
                        await send_message(
                            message=text_response, phone_number=user_phone_number
                        )
                    elif user.output_format == "audio":
                        status_audio = await translator.voice_to_voice_translator(
                            file=audio_file
                        )
                        if status_audio:
                            await send_voice_message("new.mp3", user_phone_number)
                        else:
                            await send_message(
                                message="Error processing audio file",
                                phone_number=user_phone_number,
                            )
                    else:
                        text_response = await translator.voice_to_text_translator(
                            file=audio_file, language=user.default_language
                        )
                        status_audio = await translator.voice_to_voice_translator(
                            file=audio_file, language=user.output_language
                        )
                        await send_message(
                            message=text_response, phone_number=user_phone_number
                        )
                        if status_audio:
                            await send_voice_message("new.wav", user_phone_number)
                        else:
                            await send_message(
                                message="Error processing audio file",
                                phone_number=user_phone_number,
                            )
                else:
                    signup_link = "https://signup"
                    msg = (
                        f"Welcome to Wazobia, your AI translator right here on WhatsApp, "
                        f"please click the link to signup \n{signup_link}"
                    )
                    await send_message(message=msg, phone_number=user_phone_number)
                # Clean up files
                if os.path.exists(audio_file):
                    os.remove(audio_file)
                if os.path.exists("new.mp3"):
                    os.remove("new.mp3")
            else:
                await send_message(
                    "Audio message received but no audio ID found.",
                    user_phone_number,
                )

        # Unsupported message type
        else:
            await send_message(
                "Message format not supported. Wazobia AI only supports text and audio message.",
                user_phone_number,
            )

        return PlainTextResponse("PROCESSED", status_code=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
