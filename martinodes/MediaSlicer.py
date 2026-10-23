from .shared import CATEGORY, list_head_tail

class MediaSlicer:

    @classmethod
    def INPUT_TYPES(s):
        return {
            "optional": {
                "video": ("IMAGE", {}),
                "audio": ("AUDIO", {}),
            },
            "required" : {
                "duration_seconds" : ("FLOAT", { "default" : 0.00, "step": 0.01 }),
                "video_fps" : ("FLOAT", { "default" : 24.0 }),
                "take_from" : (["start", "end"], { "default" : "end" }),
            },
        }

    RETURN_TYPES = ("IMAGE", "AUDIO")
    RETURN_NAMES = ("video", "audio")

    SEARCH_ALIASES = ["trim video", "trim audio", "slice video", "slice audio"]

    FUNCTION = "run"
    CATEGORY = CATEGORY
    DESCRIPTION = "Takes a slice with requested length from the start or the end of the loaded media. If using both audio and video, the inputs must be the same length."

    def run(self, duration_seconds, video_fps, take_from, video=None, audio=None):
        out_images = video
        out_audio = audio

        if duration_seconds < 0.001:
            return (out_images, out_audio)

        if video is not None:
            frames_to_take = int(duration_seconds * video_fps)
            out_images = list_head_tail(video, frames_to_take, take_from)

        if audio is not None:
            # ComfyUI AUDIO structure: {"waveform": tensor(batch, channels, samples), "sample_rate": int}
            waveform = audio["waveform"]
            sample_rate = audio["sample_rate"]

            samples_to_take = int(duration_seconds * sample_rate)

            # permute the waveform to (samples, batch, channels) to slice accordingly.
            # This handles batch processing "vectorially" - by moving the time dimension to the front,
            # we can slice the time for all batch items (and channels) simultaneously without a loop.
            waveform_permuted = waveform.permute(2, 0, 1)

            cut_waveform = list_head_tail(waveform_permuted, samples_to_take, take_from)

            # Restore original shape (batch, channels, samples)
            new_waveform = cut_waveform.permute(1, 2, 0)

            out_audio = {
                "waveform": new_waveform,
                "sample_rate": sample_rate
            }

        return (out_images, out_audio)