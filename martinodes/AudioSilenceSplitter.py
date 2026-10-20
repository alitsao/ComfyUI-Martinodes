import torch

from .shared import CATEGORY


class AudioSilenceSplitter:
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio": ("AUDIO", {}),
                "optimal_length": ("FLOAT", {"default": 5.0, "min": 0.1, "step": 0.1}),
                "minimal_silence": ("FLOAT", {"default": 0.3, "min": 0.05, "step": 0.05}),
                "silence_threshold_db": ("FLOAT", {"default": 35.0, "min": 1.0, "max": 100.0, "step": 1.0}),
            },
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    OUTPUT_IS_LIST = (True, False)
    SEARCH_ALIASES = ["split audio at silence", "split audio by pauses"]
    FUNCTION = "run"
    CATEGORY = CATEGORY
    DESCRIPTION = "Splits audio at the silence nearest the target fragment length."

    def run(self, audio, optimal_length=5.0, minimal_silence=0.3, silence_threshold_db=35.0):
        if audio is None:
            return (None,)
        
        waveform = audio["waveform"]
        sample_rate = audio["sample_rate"]
        fragments = []

        for batch_index in range(waveform.shape[0]):
            item = waveform[batch_index]
            sample_count = item.shape[-1]
            analysis_signal = item.detach().abs().amax(dim=0)
            silence_gaps = self.find_silence_gaps(
                analysis_signal, sample_rate, minimal_silence, silence_threshold_db
            )

            optimal_samples = max(1, int(optimal_length * sample_rate))
            start = 0

            while sample_count - start > optimal_samples:
                target = start + optimal_samples
                candidate_cuts = [
                    (gap_start + gap_end) // 2
                    for gap_start, gap_end in silence_gaps
                    if start < (gap_start + gap_end) // 2 < sample_count
                ]
                cut = min(candidate_cuts, key=lambda point: abs(point - target), default=target)

                fragments.append({
                    "waveform": waveform[batch_index:batch_index + 1, :, start:cut],
                    "sample_rate": sample_rate,
                })
                start = cut

            if start < sample_count:
                fragments.append({
                    "waveform": waveform[batch_index:batch_index + 1, :, start:sample_count],
                    "sample_rate": sample_rate,
                })

        return (fragments,)


    @staticmethod
    def find_silence_gaps(analysis_signal, sample_rate, minimal_silence, threshold_db):
        sample_count = analysis_signal.numel()
        if sample_count == 0:
            return []

        frame_length = max(1, int(sample_rate * 0.01))
        padded_sample_count = (
            (sample_count + frame_length - 1) // frame_length
        ) * frame_length
        if padded_sample_count > sample_count:
            analysis_signal = torch.cat(
                (
                    analysis_signal,
                    analysis_signal.new_zeros(padded_sample_count - sample_count),
                )
            )

        frame_rms = analysis_signal.unfold(0, frame_length, frame_length).square().mean(dim=1).sqrt()
        peak_rms = frame_rms.max()
        if peak_rms.item() == 0:
            return []

        active_frames = (frame_rms > peak_rms * 10 ** (-threshold_db / 20)).tolist()
        active_runs = []
        run_start = None
        for frame_index, is_active in enumerate(active_frames):
            if is_active and run_start is None:
                run_start = frame_index
            elif not is_active and run_start is not None:
                active_runs.append((run_start, frame_index))
                run_start = None
        if run_start is not None:
            active_runs.append((run_start, len(active_frames)))

        minimum_gap_samples = int(minimal_silence * sample_rate)
        silence_gaps = []
        for (_, previous_end), (next_start, _) in zip(active_runs, active_runs[1:]):
            gap_start = previous_end * frame_length
            gap_end = min(next_start * frame_length, sample_count)
            if gap_end - gap_start >= minimum_gap_samples:
                silence_gaps.append((gap_start, gap_end))

        return silence_gaps
    