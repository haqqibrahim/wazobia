import os
from dotenv import load_dotenv

from spitch import Spitch

load_dotenv()

SPITCH_API_KEY = os.getenv("SPITCH_API_KEY")
os.environ["SPITCH_API_KEY"] = SPITCH_API_KEY


class Translator:
    def __init__(self):
        self.client = Spitch()

    async def text_to_text_translator(self, text: str, source: str, target: str) -> str:
        translation = self.client.text.translate(
            text=text,
            source=source,
            target=target,
        )
        print(f"Spitch message: {translation.text}")
        return translation.text

    async def voice_to_text_translator(self, file: str, language) -> str:
        with open(file, "rb") as f:
            translation = self.client.speech.transcribe(language=language, content=f.read())
            print(f"Text: {translation.text}")
            return translation.text

    async def text_to_voice_translator(self, text: str, language) -> bool:
        try:
            with open("new.wav", "wb") as f:
                response = self.client.speech.generate(text=text, language=language, voice="sade")
                f.write(response.read())
                print("Audio file saved as 'new.wav'")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    async def voice_to_voice_translator(self, file: str, language) -> bool:
        try:
            with open(file, "rb") as f:
                text_translation = self.client.speech.transcribe(language=language, content=f.read())

            with open("new.wav", "wb") as f:
                response = self.client.speech.generate(
                    text=text_translation.text, language="yo", voice="sade"
                )
                f.write(response.read())
                print("Audio file saved as 'new.wav'")

            return True

        except Exception as e:
            print(f"Error: {e}")
            return False
