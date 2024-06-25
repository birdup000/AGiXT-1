import asyncio
import os
from pathlib import Path
import subprocess

try:
    import google.generativeai as genai  # Primary import attempt
except ImportError:
    import sys

    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "google-generativeai"]
    )
    import google.generativeai as genai  # Import again after installation

try:
    from gtts import gTTS
except ImportError:
    import sys

    subprocess.check_call([sys.executable, "-m", "pip", "install", "gTTS"])
    from gtts import gTTS

import uuid
from Globals import getenv


class GoogleProvider:
    def __init__(
        self,
        GOOGLE_API_KEY: str = "None",
        AI_MODEL: str = "gemini-pro",
        MAX_TOKENS: int = 4000,
        AI_TEMPERATURE: float = 0.7,
        **kwargs,
    ):
        self.requirements = ["google-generativeai", "gTTS", "pydub"]
        self.GOOGLE_API_KEY = GOOGLE_API_KEY
        self.AI_MODEL = AI_MODEL
        self.MAX_TOKENS = MAX_TOKENS
        self.AI_TEMPERATURE = AI_TEMPERATURE

    @staticmethod
    def services():
        return ["llm", "tts", "vision"]

    async def inference(self, prompt, tokens: int = 0, images: list = []):
        if not self.GOOGLE_API_KEY or self.GOOGLE_API_KEY == "None":
            return "Please set your Google API key in the Agent Management page."
        try:
            genai.configure(api_key=self.GOOGLE_API_KEY)
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=new_max_tokens, temperature=float(self.AI_TEMPERATURE)
            )
            model = genai.GenerativeModel(
                model_name=self.AI_MODEL if not images else "gemini-pro-vision",
                generation_config=generation_config,
            )
            new_max_tokens = int(self.MAX_TOKENS) - tokens
            new_prompt = []
            if images:
                for image in images:
                    file_extension = Path(image).suffix
                    new_prompt.append(
                        {
                            "mime_type": f"image/{file_extension}",
                            "data": Path(image).read_bytes(),
                        }
                    )
                new_prompt.append(prompt)
                prompt = new_prompt
            response = await asyncio.to_thread(
                model.generate_content,
                contents=prompt,
                generation_config=generation_config,
            )
            if response.parts:
                generated_text = "".join(part.text for part in response.parts)
            else:
                generated_text = "".join(
                    part.text for part in response.candidates[0].content.parts
                )
            return generated_text
        except Exception as e:
            return f"Gemini Error: {e}"

    async def text_to_speech(self, text: str):
        # Generate MP3 using gTTS
        tts = gTTS(text)
        mp3_path = os.path.join(os.getcwd(), "WORKSPACE", f"{uuid.uuid4()}.mp3")
        tts.save(mp3_path)
        file_name = os.path.basename(mp3_path)
        output_url = f"{getenv('AGIXT_URI')}/outputs/{file_name}"
        return output_url
