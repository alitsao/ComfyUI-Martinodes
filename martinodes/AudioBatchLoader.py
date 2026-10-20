import os
import folder_paths
from comfy_extras.nodes_audio import load as load_audio
from .shared import CATEGORY


class AudioBatchLoader:
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_path": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    OUTPUT_IS_LIST = (True,)
    SEARCH_ALIASES = ["load audio folder", "audio files"]
    FUNCTION = "load"
    CATEGORY = CATEGORY
    DESCRIPTION = "Loads audio files directly from a folder in ascending filename order."


    @staticmethod
    def resolve_folder(input_path):
        input_path = input_path.strip()
        if os.path.isabs(input_path):
            return input_path
        return os.path.join(folder_paths.get_input_directory(), input_path)


    @staticmethod
    def list_files(folder):
        return sorted(
            filename
            for filename in folder_paths.filter_files_content_types(os.listdir(folder), ["audio"])
            if os.path.isfile(os.path.join(folder, filename))
        )


    @classmethod
    def IS_CHANGED(cls, input_path):
        folder = cls.resolve_folder(input_path)
        if not os.path.isdir(folder):
            return ""
        return str([
            (filename, os.path.getmtime(os.path.join(folder, filename)))
            for filename in cls.list_files(folder)
        ])


    def load(self, input_path):
        folder = self.resolve_folder(input_path)
        if not os.path.isdir(folder):
            raise FileNotFoundError(f"AudioBatchLoader: Folder not found: '{folder}'")

        files = self._list_files(folder)
        if not files:
            raise FileNotFoundError(f"AudioBatchLoader: No audio files in '{folder}'")

        audios = []
        for filename in files:
            waveform, sample_rate = load_audio(os.path.join(folder, filename))
            audios.append({
                "waveform": waveform.unsqueeze(0),
                "sample_rate": sample_rate,
            })

        return (audios,)
