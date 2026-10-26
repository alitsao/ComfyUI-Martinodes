import os
import folder_paths
from comfy_extras.nodes_audio import load as load_audio
from .shared import CATEGORY


class AudioLoader:
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_path": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    OUTPUT_IS_LIST = (True,)
    SEARCH_ALIASES = ["load audio", "audio file"]
    FUNCTION = "run"
    CATEGORY = CATEGORY
    DESCRIPTION = "Loads audio file into memory."


    @staticmethod
    def resolve_folder(input_path=""):
        input_path = input_path.strip()
        if os.path.isabs(input_path):
            return input_path
        return os.path.join(folder_paths.get_input_directory(), input_path)


    def run(self, file_path):
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"AudioLoader: File not found: '{file_path}'")

        audios = []
        waveform, sample_rate = load_audio(file_path)
        audios.append({
            "waveform": waveform.unsqueeze(0),
            "sample_rate": sample_rate,
        })

        return (audios,)
