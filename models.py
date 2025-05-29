import os
from dotenv import load_dotenv
from spitch import Spitch
import ffmpeg

# Load environment variables from a .env file
load_dotenv()

# Retrieve and set the Spitch API key
SPITCH_API_KEY = os.getenv("SPITCH_API_KEY")
os.environ["SPITCH_API_KEY"] = SPITCH_API_KEY


class Translator:
    """
    Translator class provides methods for translating text and speech
    between different languages using the Spitch API. It also includes
    methods for converting audio files to different formats.
    """

    def __init__(self):
        """
        Initializes the Translator with a Spitch client.
        """
        self.client = Spitch()

    async def text_to_text_translator(self, text: str, source: str, target: str) -> str:
        """
        Translates text from the source language to the target language.

        Args:
            text (str): The text to translate.
            source (str): The source language code.
            target (str): The target language code.

        Returns:
            str: The translated text.
        """
        translation = self.client.text.translate(
            text=text,
            source=source,
            target=target,
        )
        print(f"Spitch message: {translation.text}")
        return translation.text

    async def voice_to_text_translator(
        self, file_path: str, default_language: str, output_language: str
    ) -> str:
        """
        Transcribes speech from an audio file and translates the resulting text.

        Args:
            file_path (str): Path to the audio file.
            default_language (str): Language code of the audio.
            output_language (str): Target language code for translation.

        Returns:
            str: The translated text.
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, "rb") as audio_file:
            print(default_language, output_language)
            voice_translation = self.client.speech.transcribe(
                language=default_language, content=audio_file.read()
            )
            print(f"Transcribed Text: {voice_translation.text}")

            translation = self.client.text.translate(
                text=voice_translation.text,
                source=default_language,
                target=output_language,
            )
        print(f"Spitch message: {translation.text}")
        return translation.text

    async def text_to_voice_translator(
        self, text: str, input_language: str, output_language: str
    ) -> bool:
        """
        Translates text and generates speech in the output language.

        Args:
            text (str): The text to translate and synthesize.
            input_language (str): Source language code.
            output_language (str): Target language code.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            text_translation = self.client.text.translate(
                text=text,
                source=input_language,
                target=output_language,
            )

            # Select voice based on output language
            voice_map = {
                "en": "lucy",
                "yo": "sade",
                "ig": "amara",
                "ha": "amina"
            }
            voice = voice_map.get(output_language, "lucy")

            # Generate speech and save as WAV
            with open("new.wav", "wb") as audio_file:
                response = self.client.speech.generate(
                    text=text_translation.text, language=output_language, voice=voice
                )
                audio_file.write(response.read())
                print("Audio file saved as 'new.wav'")

            # Convert WAV to MP3
            if self.convert_audio_to_mp3("new.wav", "new.mp3"):
                print("Audio file converted to 'new.mp3'")
                return True
            else:
                print("Audio conversion failed.")
                return False

        except Exception as e:
            print(f"Error: {e}")
            return False

    async def voice_to_voice_translator(
        self, file_path: str, default_language: str, output_language: str
    ) -> bool:
        """
        Transcribes speech from an audio file, translates it, and generates
        speech in the target language.

        Args:
            file_path (str): Path to the audio file.
            default_language (str): Source language code.
            output_language (str): Target language code.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not os.path.isfile(file_path):
            print(f"File not found: {file_path}")
            return False

        try:
            with open(file_path, "rb") as audio_file:
                text_translation = self.client.speech.transcribe(
                    language=default_language, content=audio_file.read()
                )

            translated_text = self.client.text.translate(
                text=text_translation.text,
                source=default_language,
                target=output_language,
            )

            # Select voice based on output language
            voice_map = {
                "en": "lucy",
                "yo": "sade",
                "ig": "amara",
                "ha": "amina"
            }
            voice = voice_map.get(output_language, "sade")

            with open("new.wav", "wb") as audio_file:
                response = self.client.speech.generate(
                    text=translated_text.text,
                    language=output_language,
                    voice=voice,
                )
                audio_file.write(response.read())
                print("Audio file saved as 'new.wav'")

            return True

        except Exception as e:
            print(f"Error: {e}")
            return False

    def convert_audio_to_mp3(
        self, input_file: str, output_file: str = "new.mp3"
    ) -> bool:
        """
        Converts an audio file to MP3 format using ffmpeg-python.

        Args:
            input_file (str): Path to the input audio file.
            output_file (str): Path to the output MP3 file.

        Returns:
            bool: True if conversion is successful, False otherwise.
        """
        if not os.path.isfile(input_file):
            print(f"Input file does not exist: {input_file}")
            return False

        try:
            (
                ffmpeg.input(input_file)
                .output(output_file, format="mp3", audio_bitrate="192k")
                .run(overwrite_output=True, quiet=True)
            )
            print(f"Converted {input_file} to {output_file}")
            return True
        except ffmpeg.Error as e:
            print(f"ffmpeg error: {e}")
            return False
