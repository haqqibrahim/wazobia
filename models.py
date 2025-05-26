import os
from dotenv import load_dotenv

from spitch import Spitch
import ffmpeg  # Add this import

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

    async def voice_to_text_translator(
        self, file: str, default_language, output_language
    ) -> str:
        with open(file, "rb") as f:
            print(default_language, output_language)
            voice_translation = self.client.speech.transcribe(
                language=default_language, content=f.read()
            )
            print(f"Text: {voice_translation.text}")

            translation = self.client.text.translate(
                text=voice_translation.text,
                source=default_language,
                target=output_language,
            )
        print(f"Spitch message: {translation.text}")
        return translation.text

    async def text_to_voice_translator(
        self, text: str, input_language, output_language
    ) -> bool:
        try:
            text_translation = self.client.text.translate(
                text=text,
                source=input_language,
                target=output_language,
            )
            if output_language == "en":
                voice = "lucy"
            
            if output_language == "yo":
                voice = "sade"

            if output_language == "ig":
                voice = "amara"

            if output_language == "ha":
                voice = "amina"
                
            with open("new.wav", "wb") as f:
                response = self.client.speech.generate(
                    text=text_translation.text, language=output_language, voice=voice
                )
                f.write(response.read())
                print("Audio file saved as 'new.wav'")

                # Convert
                self.convert_audio_to_wav("new.wav")
                print("Audio file converted to 'new.mp3'")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    async def voice_to_voice_translator(
        self, file: str, default_language, output_language
    ) -> bool:
        try:
            with open(file, "rb") as f:
                text_translation = self.client.speech.transcribe(
                    language=default_language, content=f.read()
                )

            text_translation_lang = self.client.text.translate(
                text=text_translation.text,
                source=default_language,
                target=output_language,
            )

            with open("new.wav", "wb") as f:
                response = self.client.speech.generate(
                    text=text_translation_lang.text,
                    language=output_language,
                    voice="sade",
                )
                f.write(response.read())
                print("Audio file saved as 'new.wav'")

            return True

        except Exception as e:
            print(f"Error: {e}")
            return False

    def convert_audio_to_wav(
        self, input_file: str, output_file: str = "new.mp3"
    ) -> bool:
        """
        Converts an audio file to WAV format using ffmpeg-python.
        """
        try:
            (
                ffmpeg.input(input_file)
                .output(output_file, format="mp3", audio_bitrate="192k")
                .run(overwrite_output=True)
            )
            print(f"Converted {input_file} to {output_file}")
            return True
        except ffmpeg.Error as e:
            print(f"ffmpeg error: {e}")
            return False
