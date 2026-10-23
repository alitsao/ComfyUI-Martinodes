from .shared import CATEGORY, resample_audio

class AudioResampler:

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "audio": ("AUDIO", {}),
                "samplerate" : ("INT", { "default" : 44100, "min": 8000, "max": 96000 }),
                "channels" : ("INT", { "default" : 1, "min": 1, "max": 2 })
            },
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)

    SEARCH_ALIASES = ["resample audio"]

    FUNCTION = "run"
    CATEGORY = CATEGORY
    DESCRIPTION = "Resamples audio to the target samplerate and channels. Useful when concatenating audios from different sources."

    def run(self, audio, samplerate, channels):
        if channels < 1 or channels > 2:
             raise Exception("Only 1 or 2 channels are supported.")
       
        # ComfyUI AUDIO structure: {"waveform": tensor(batch, channels, samples), "sample_rate": int}
        if audio is None:
             raise Exception("No audio provided to resample.")

        out_audio = resample_audio(audio, samplerate, channels)

        return (out_audio,)
