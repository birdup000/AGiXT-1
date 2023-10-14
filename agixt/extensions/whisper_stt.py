try:
    from whispercppy import Whisper
except ImportError:
    import sys
    import subprocess

    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "whispercppy",
        ]
    )
    from whispercppy import Whisper

import base64
import os
from Extensions import Extensions


class whisper_stt(Extensions):
    def __init__(self, WHISPER_MODEL="base.en", **kwargs):
        self.commands = {
            "Transcribe Audio from File": self.transcribe_audio_from_file,
            "Transcribe Base64 Audio": self.transcribe_base64_audio,
        }
        # https://huggingface.co/ggerganov/whisper.cpp
        # Models: tiny, tiny.en, base, base.en, small, small.en, medium, medium.en, large, large-v1
        if WHISPER_MODEL not in [
            "tiny",
            "tiny.en",
            "base",
            "base.en",
            "small",
            "small.en",
            "medium",
            "medium.en",
            "large",
            "large-v1",
        ]:
            self.WHISPER_MODEL = "base.en"
        else:
            self.WHISPER_MODEL = WHISPER_MODEL
        os.makedirs(os.path.join(os.getcwd(), "models", "whispercpp"), exist_ok=True)
        model_path = os.path.join(
            os.getcwd(), "models", "whispercpp", f"ggml-{WHISPER_MODEL}-q5_1.bin"
        )
        self.model_path = model_path

    async def transcribe_audio_from_file(self, filename: str = "recording.wav"):
        w = Whisper.from_pretrained(
            model_name=self.WHISPER_MODEL.lower(), basedir=self.model_path
        )
        file_path = os.path.join(os.getcwd(), "WORKSPACE", filename)
        if not os.path.exists(file_path):
            raise RuntimeError(f"Failed to load audio: {filename} does not exist.")
        output = w.transcribe_from_file(file_path)
        return output

    async def transcribe_base64_audio(self, base64_audio: str):
        # Save the audio as a file then run transcribe_audio_from_file.
        audio = base64.b64decode(base64_audio)
        filename = "recording.wav"
        with open(filename, "wb") as f:
            f.write(audio)
        output = self.transcribe_audio_from_file(filename)
        os.remove(filename)
        return output
