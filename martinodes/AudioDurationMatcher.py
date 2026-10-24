from .shared import CATEGORY
import torch

class AudioDurationMatcher:

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "audio": ("AUDIO", {}),
                "duration_seconds" : ("FLOAT", { "default" : 0.00, "step": 0.01 }),
                "pad" : (["start", "end"], { "default" : "end" }),
                "crop" : (["start", "end"], { "default" : "end" }),
            },
            "optional": {
                "fps": ("FLOAT", {"default": 24.0, "min": 1.0, "max": 120.0, "step": 1.0}),
                "duration_frames": ("INT", {"default": 0, "min": 0}),
            },
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)

    SEARCH_ALIASES = ["pad audio", "crop audio"]

    FUNCTION = "run"
    CATEGORY = CATEGORY
    DESCRIPTION = "Makes audio to have the specified duration, cropping or padding as needed."


    def run(self, audio, duration_seconds=0.0, pad="end", crop="end", fps=24.0, duration_frames=0):
        if duration_seconds == 0:
            if fps <= 0:
                raise ValueError("fps must be greater than zero when duration_seconds is 0.")
            duration_seconds = duration_frames / fps

        # ComfyUI AUDIO structure: {"waveform": tensor(batch, channels, samples), "sample_rate": int}
        if audio is None:
             raise Exception("No audio provided to process.")

        waveform = audio["waveform"]
        sr = audio["sample_rate"]
        device = waveform.device

        batch_size = waveform.shape[0]
        processed_batch = []

        target_samples = int(duration_seconds * sr)

        for b in range(batch_size):
            item = waveform[b]
            current_samples = item.shape[-1]

            if current_samples == target_samples:
                processed_batch.append(item)
                continue

            if current_samples > target_samples:
                if crop == "start":
                    processed = item[..., current_samples - target_samples:]
                else:
                    processed = item[..., :target_samples]
            else:
                pad_amount = target_samples - current_samples
                silence = torch.zeros((item.shape[0], pad_amount), device=device, dtype=item.dtype)
                if pad == "start":
                    processed = torch.cat((silence, item), dim=-1)
                else:
                    processed = torch.cat((item, silence), dim=-1)

            processed_batch.append(processed)

        # Stack back into a batch tensor
        out_tensor = torch.stack(processed_batch).to(device)

        out_audio = {
            "waveform": out_tensor,
            "sample_rate": sr
        }

        return (out_audio,)
