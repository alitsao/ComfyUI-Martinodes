from .shared import CATEGORY


class MediaSlicer:

    @classmethod
    def INPUT_TYPES(s):
        return {
            "optional": {
                "video": ("IMAGE", {}),
                "audio": ("AUDIO", {}),
            },
            "required": {
                "start_offset_seconds": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 3600.0, "step": 0.1}),
                "end_offset_seconds": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 3600.0, "step": 0.1}),
                "end_offset_from": (["end", "start"], {"default": "end"}),
                "video_fps": ("FLOAT", {"default": 24.0, "min": 1.0, "max": 120.0, "step": 1.0}),
            },
        }

    RETURN_TYPES = ("IMAGE", "AUDIO")
    RETURN_NAMES = ("video", "audio")

    SEARCH_ALIASES = ["trim video", "trim audio", "slice video", "slice audio"]

    FUNCTION = "run"
    CATEGORY = CATEGORY
    DESCRIPTION = "Slices video and/or audio between a start offset and an end offset. The end offset is measured from the end by default, or from the start when selected."

    def run(self, start_offset_seconds=0.0, end_offset_seconds=0.0, end_offset_from="end", video_fps=24.0, video=None, audio=None):
        out_images = video
        out_audio = audio

        if video is not None:
            total_frames = video.shape[0]
            start_frame = min(max(int(start_offset_seconds * video_fps), 0), total_frames)
            if end_offset_from == "start":
                end_frame = min(max(int(end_offset_seconds * video_fps), 0), total_frames)
            else:
                end_frame = min(max(total_frames - int(end_offset_seconds * video_fps), 0), total_frames)

            if start_frame >= end_frame:
                raise ValueError(
                    f"MediaSlicer: Calculated start video frame ({start_frame}) is >= "
                    f"end video frame ({end_frame}) (total video frames: {total_frames})."
                )
            out_images = video[start_frame:end_frame]

        if audio is not None:
            waveform = audio["waveform"]
            sample_rate = audio["sample_rate"]
            total_samples = waveform.shape[-1]
            start_sample = min(max(int(start_offset_seconds * sample_rate), 0), total_samples)
            if end_offset_from == "start":
                end_sample = min(max(int(end_offset_seconds * sample_rate), 0), total_samples)
            else:
                end_sample = min(max(total_samples - int(end_offset_seconds * sample_rate), 0), total_samples)

            if start_sample >= end_sample:
                raise ValueError(
                    f"MediaSlicer: Calculated start audio sample ({start_sample}) is >= "
                    f"end audio sample ({end_sample}) (total audio samples: {total_samples})."
                )
            out_audio = {
                "waveform": waveform[..., start_sample:end_sample],
                "sample_rate": sample_rate,
            }

        return (out_images, out_audio)
