from .shared import CATEGORY, resample_audio
import torch

class MediaOverlappingConcatenator:

    @classmethod
    def INPUT_TYPES(s):
        return {
            "optional": {
                "video_1": ("IMAGE", {}),
                "audio_1": ("AUDIO", {}),
                "video_2": ("IMAGE", {}),
                "audio_2": ("AUDIO", {}),
            },
            "required" : {
                "video_fps" : ("FLOAT", { "default" : 24.0 }),
                "overlap_duration_seconds" : ("FLOAT", { "default" : 0.0 }),
                "video_overlap_resolve" : (["video_1", "video_2", "crossfade"], { "default" : "crossfade" }),
                "audio_overlap_resolve" : (["audio_1", "audio_2", "crossfade"], { "default" : "crossfade" }),
            },
        }

    RETURN_TYPES = ("IMAGE", "AUDIO")
    RETURN_NAMES = ("video", "audio")

    SEARCH_ALIASES = ["concatenate video", "concatenate audio", "join videos", "join audio"]

    FUNCTION = "run"
    CATEGORY = CATEGORY
    DESCRIPTION = "Concatenates two videos and / or audios, applying overlapping logic."

    def run(
        self,
        video_fps,
        overlap_duration_seconds,
        video_overlap_resolve,
        audio_overlap_resolve,
        video_1=None,
        audio_1=None,
        video_2=None,
        audio_2=None,
    ):
        out_images = None
        if video_1 is not None and len(video_1) > 0 and video_2 is not None and len(video_2) > 0:
             overlap_frames_count = int(overlap_duration_seconds * video_fps)
             
             min_len = min(len(video_1), len(video_2))
             if overlap_frames_count > min_len:
                  overlap_frames_count = min_len

             if overlap_frames_count <= 0:
                 out_images = torch.cat((video_1, video_2), dim=0)
             else:
                 pre_overlap = video_1[:-overlap_frames_count]
                 post_overlap = video_2[overlap_frames_count:]
                 
                 overlap_1 = video_1[-overlap_frames_count:]
                 overlap_2 = video_2[:overlap_frames_count]
                 
                 if video_overlap_resolve == "video_1":
                     overlap_part = overlap_1
                 elif video_overlap_resolve == "video_2":
                     overlap_part = overlap_2
                 else: # crossfade
                     device = video_1.device
                     alpha = torch.linspace(0, 1, overlap_frames_count, device=device).view(-1, 1, 1, 1)
                     # Linear interpolation
                     overlap_part = overlap_1 * (1.0 - alpha) + overlap_2 * alpha
                 
                 # Combine: pre_overlap + overlap_part + post_overlap
                 out_images = torch.cat((pre_overlap, overlap_part, post_overlap), dim=0)

        elif video_1 is not None and len(video_1) > 0:
            out_images = video_1
        elif video_2 is not None and len(video_2) > 0:
            out_images = video_2
        
        out_audio = None
        if audio_1 and audio_2:
            sr1 = audio_1["sample_rate"]
            sr2 = audio_2["sample_rate"]
            target_sr = max(sr1, sr2)
            
            chan1 = audio_1["waveform"].shape[1]
            chan2 = audio_2["waveform"].shape[1]
            target_channels = max(chan1, chan2)
            
            if sr1 != target_sr or chan1 != target_channels:
                audio_1 = resample_audio(audio_1, target_sr, target_channels)
            
            if sr2 != target_sr or chan2 != target_channels:
                audio_2 = resample_audio(audio_2, target_sr, target_channels)

            sr = target_sr
            wave_1 = audio_1["waveform"]
            wave_2 = audio_2["waveform"]
            
            overlap_samples_count = int(overlap_duration_seconds * sr)
            
            min_samples = min(wave_1.shape[-1], wave_2.shape[-1])
            if overlap_samples_count > min_samples:
                overlap_samples_count = min_samples

            if overlap_samples_count <= 0:
                 out_wave = torch.cat((wave_1, wave_2), dim=-1)
            else:
                pre_overlap = wave_1[..., :-overlap_samples_count]
                # Note: post_overlap starts after the overlap region in the second clip
                post_overlap = wave_2[..., overlap_samples_count:]
                
                overlap_1 = wave_1[..., -overlap_samples_count:]
                overlap_2 = wave_2[..., :overlap_samples_count]
                
                if audio_overlap_resolve == "audio_1":
                    overlap_part = overlap_1
                elif audio_overlap_resolve == "audio_2":
                    overlap_part = overlap_2
                else: # crossfade
                    device = wave_1.device
                    # Shape (1, 1, Samples) or (1, Samples) depending on dimensions needed to broadcast
                    # Waveform is (Batch, Channels, Samples)
                    alpha = torch.linspace(0, 1, overlap_samples_count, device=device).view(1, 1, -1)
                    overlap_part = overlap_1 * (1.0 - alpha) + overlap_2 * alpha
                
                out_wave = torch.cat((pre_overlap, overlap_part, post_overlap), dim=-1)
            
            out_audio = {"waveform": out_wave, "sample_rate": sr}

        elif audio_1:
            out_audio = audio_1
        elif audio_2:
            out_audio = audio_2

        return (out_images, out_audio)
