import comfy.audio
import torch

CATEGORY = "martinodes"

MINIMAX_H3_PARAMS = {
    "audio_token_rate": 40,
    "frame_multi": 17.0,
    "frame_offset": 5.0,
    "min_latent_temporal_tokens": 2.0
}


def list_head_tail(list, take_count, start_end):

    total = list.shape[0]
    take_count = min(take_count, total)

    if start_end == "start":
        new_list = list[:take_count]
    else:
        new_list = list[-take_count:]

    return new_list


def resample_audio(audio, samplerate, channels):
    waveform = audio["waveform"]
    orig_sr = audio["sample_rate"]

    if orig_sr != samplerate:
        waveform = comfy.audio.resample(waveform, orig_sr, samplerate)

    current_channels = waveform.shape[1]
    if current_channels > channels:
        waveform = waveform[:, :channels, :]
    elif current_channels < channels:
        last_channel = waveform[:, -1:, :].expand(-1, channels - current_channels, -1)
        waveform = torch.cat((waveform, last_channel), dim=1)

    out_audio = {
        "waveform": waveform,
        "sample_rate": samplerate
    }

    return out_audio
