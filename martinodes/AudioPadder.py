import torch

from .shared import CATEGORY


class AudioPadder:

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "audio": ("AUDIO", {}),
                "pad_start_seconds": ("FLOAT", {"default": 0.0, "min": 0.0, "step": 0.01}),
                "pad_end_seconds": ("FLOAT", {"default": 0.0, "min": 0.0, "step": 0.01}),
            },
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)

    SEARCH_ALIASES = ["pad audio", "add silence"]

    FUNCTION = "run"
    CATEGORY = CATEGORY
    DESCRIPTION = "Adds silence to the start and end of audio."

    def run(self, audio, pad_start_seconds=0.0, pad_end_seconds=0.0):
        if audio is None:
            raise ValueError("No audio provided to pad.")
        if pad_start_seconds < 0 or pad_end_seconds < 0:
            raise ValueError("Padding durations must be non-negative.")

        waveform = audio["waveform"]
        sample_rate = audio["sample_rate"]
        start_samples = int(pad_start_seconds * sample_rate)
        end_samples = int(pad_end_seconds * sample_rate)

        start_silence = waveform.new_zeros((*waveform.shape[:-1], start_samples))
        end_silence = waveform.new_zeros((*waveform.shape[:-1], end_samples))
        padded_waveform = torch.cat((start_silence, waveform, end_silence), dim=-1)

        return ({
            "waveform": padded_waveform,
            "sample_rate": sample_rate,
        },)
