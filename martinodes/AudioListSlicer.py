from .shared import CATEGORY


class AudioListSlicer:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio": ("AUDIO", {}),
                "slice_duration": ("FLOAT", {"default": 5.0, "min": 0.01, "step": 0.01}),
            },
            "optional": {
                "first_slice_duration": ("FLOAT", {"default": 0.0, "min": 0.0, "step": 0.01}),
            },
        }

    RETURN_TYPES = ("AUDIO", "INT")
    RETURN_NAMES = ("slices", "list_length")
    OUTPUT_IS_LIST = (True, False)
    FUNCTION = "run"
    CATEGORY = CATEGORY
    DESCRIPTION = "Splits audio into consecutive slices, with an optional duration for the first slice."

    def run(self, audio, slice_duration, first_slice_duration=0.0):
        if audio is None:
            raise ValueError("No audio provided.")
        if slice_duration <= 0:
            raise ValueError("slice_duration must be greater than zero.")

        waveform = audio["waveform"]
        sample_rate = audio["sample_rate"]
        default_samples = max(1, int(slice_duration * sample_rate))
        first_samples = (
            max(1, int(first_slice_duration * sample_rate))
            if first_slice_duration is not None and first_slice_duration > 0
            else default_samples
        )

        slices = []
        for batch_index in range(waveform.shape[0]):
            sample_count = waveform.shape[-1]
            start = 0
            next_slice_samples = first_samples

            while start < sample_count:
                end = min(start + next_slice_samples, sample_count)
                slices.append({
                    "waveform": waveform[batch_index:batch_index + 1, :, start:end],
                    "sample_rate": sample_rate,
                })
                start = end
                next_slice_samples = default_samples

        return (slices, len(slices))