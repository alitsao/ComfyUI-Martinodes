import torch
from .shared import CATEGORY, MINIMAX_H3_PARAMS
from .latentops import align_duration_to_tokens


class LatentOverlappingConcatenator:

    @classmethod
    def INPUT_TYPES(s):
        return {
            "optional": {
                "av_latent_1": ("LATENT", {}),
                "av_latent_2": ("LATENT", {}),
            },
            "required": {
                "video_fps": ("FLOAT", {"default": 24.0, "min": 1.0, "max": 120.0, "step": 1.0}),
                "overlap_duration_seconds": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 60.0, "step": 0.1}),
                "video_overlap_resolve": (["av_latent_1", "av_latent_2", "crossfade"], {"default": "crossfade"}),
                "audio_overlap_resolve": (["av_latent_1", "av_latent_2", "crossfade"], {"default": "crossfade"}),
            },
        }

    RETURN_TYPES = ("LATENT", )
    RETURN_NAMES = ("av_latent", )

    SEARCH_ALIASES = ["concatenate latent", "concatenate video audio latent", "join av latents"]

    FUNCTION = "run"
    CATEGORY = CATEGORY
    DESCRIPTION = "Concatenates two video+audio latents, applying overlapping logic."

    def run(self, video_fps, overlap_duration_seconds, video_overlap_resolve, audio_overlap_resolve, av_latent_1=None, av_latent_2=None):
        out_av = concat_av_latents(video_fps, overlap_duration_seconds, video_overlap_resolve, audio_overlap_resolve, av_latent_1, av_latent_2)
        return (out_av, )


class LatentListOverlappingConcatenator:
    # Maps UI options to the pairwise resolve names used by concat_av_latents
    RESOLVE_MAP = {"previous": "av_latent_1", "next": "av_latent_2", "crossfade": "crossfade"}
    INPUT_IS_LIST = True

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "av_latents": ("LATENT", {}),
                "video_fps": ("FLOAT", {"default": 24.0, "min": 1.0, "max": 120.0, "step": 1.0}),
                "overlap_duration_seconds": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 60.0, "step": 0.1}),
                "video_overlap_resolve": (["previous", "next", "crossfade"], {"default": "crossfade"}),
                "audio_overlap_resolve": (["previous", "next", "crossfade"], {"default": "crossfade"}),
            },
        }

    RETURN_TYPES = ("LATENT", )
    RETURN_NAMES = ("av_latent", )

    SEARCH_ALIASES = ["concatenate latent list", "join av latents", "concatenate video audio latent list"]

    FUNCTION = "run"
    CATEGORY = CATEGORY
    DESCRIPTION = "Concatenates a list of video+audio latents, applying overlapping logic in list order."

    def run(self, av_latents, video_fps, overlap_duration_seconds, video_overlap_resolve, audio_overlap_resolve):
        video_fps = video_fps[0] if isinstance(video_fps, list) else video_fps
        overlap_duration_seconds = (
            overlap_duration_seconds[0]
            if isinstance(overlap_duration_seconds, list)
            else overlap_duration_seconds
        )
        video_overlap_resolve = (
            video_overlap_resolve[0]
            if isinstance(video_overlap_resolve, list)
            else video_overlap_resolve
        )
        audio_overlap_resolve = (
            audio_overlap_resolve[0]
            if isinstance(audio_overlap_resolve, list)
            else audio_overlap_resolve
        )
        if not av_latents:
            return (None, )

        video_resolve = self.RESOLVE_MAP[video_overlap_resolve]
        audio_resolve = self.RESOLVE_MAP[audio_overlap_resolve]
        out_av = av_latents[0]
        for av_latent in av_latents[1:]:
            out_av = concat_av_latents(
                video_fps,
                overlap_duration_seconds,
                video_resolve,
                audio_resolve,
                av_latent_1=out_av,
                av_latent_2=av_latent,
            )
        return (out_av, )



def concat_av_latents(video_fps, overlap_duration_seconds, video_overlap_resolve, audio_overlap_resolve, av_latent_1=None, av_latent_2=None):
    if av_latent_1 is None and av_latent_2 is None:
        return None
    if av_latent_1 is None:
        return av_latent_2
    if av_latent_2 is None:
        return av_latent_1

    # Convert requested overlap duration into latent token counts using the same
    # snapping rules the extender uses, so overlaps stay aligned to the model's temporal compression.
    video_overlap_tokens = 0
    audio_overlap_tokens = 0

    video_overlap_tokens, audio_overlap_tokens = align_duration_to_tokens(overlap_duration_seconds, video_fps, MINIMAX_H3_PARAMS)

    samples_1 = av_latent_1["samples"]
    samples_2 = av_latent_2["samples"]

    video_1, audio_1 = samples_1.unbind()
    video_2, audio_2 = samples_2.unbind()

    dims_v = len(video_1.shape)
    t_dim_v = 2 if dims_v >= 3 else 0
    dims_a = len(audio_1.shape)
    t_dim_a = -1

    video_overlap_tokens = min(video_overlap_tokens, video_1.shape[t_dim_v], video_2.shape[t_dim_v])
    audio_overlap_tokens = min(audio_overlap_tokens, audio_1.shape[t_dim_a], audio_2.shape[t_dim_a])

    combined_v = concat_with_overlap(video_1, video_2, dims_v, t_dim_v, video_overlap_tokens, video_overlap_resolve)
    combined_a = concat_with_overlap(audio_1, audio_2, dims_a, t_dim_a, audio_overlap_tokens, audio_overlap_resolve)

    out_av = av_latent_1.copy()
    out_av["samples"] = type(samples_1)([combined_v, combined_a])
    out_av.pop("noise_mask", None)

    return out_av


def concat_with_overlap(tensor_1, tensor_2, dims, t_dim, overlap_tokens, resolve_method):
    if overlap_tokens <= 0:
        return torch.cat((tensor_1, tensor_2), dim=t_dim)

    idx_pre = [slice(None)] * dims
    idx_pre[t_dim] = slice(None, -overlap_tokens)
    idx_post = [slice(None)] * dims
    idx_post[t_dim] = slice(overlap_tokens, None)
    idx_ov1 = [slice(None)] * dims
    idx_ov1[t_dim] = slice(-overlap_tokens, None)
    idx_ov2 = [slice(None)] * dims
    idx_ov2[t_dim] = slice(None, overlap_tokens)

    pre = tensor_1[tuple(idx_pre)]
    post = tensor_2[tuple(idx_post)]
    overlap_1 = tensor_1[tuple(idx_ov1)]
    overlap_2 = tensor_2[tuple(idx_ov2)]

    if resolve_method == "av_latent_1":
        overlap_part = overlap_1
    elif resolve_method == "av_latent_2":
        overlap_part = overlap_2
    else:  # crossfade
        alpha_shape = [1] * dims
        alpha_shape[t_dim] = overlap_tokens
        alpha = torch.linspace(0, 1, overlap_tokens, device=tensor_1.device).view(alpha_shape)
        overlap_part = overlap_1 * (1.0 - alpha) + overlap_2 * alpha

    return torch.cat((pre, overlap_part, post), dim=t_dim)
    