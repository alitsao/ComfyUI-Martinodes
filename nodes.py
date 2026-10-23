from .martinodes.MediaSlicer import MediaSlicer
from .martinodes.AudioResampler import AudioResampler
from .martinodes.AudioTrimExtender import AudioTrimExtender
from .martinodes.AudioInfo import AudioInfo
from .martinodes.AudioLoader import AudioLoader
from .martinodes.AudioSilenceSplitter import AudioSilenceSplitter
from .martinodes.AudioIterator import AudioIterator
from .martinodes.LatentAVInfo import LatentAVInfo
from .martinodes.MediaOverlappingConcatenator import MediaOverlappingConcatenator
from .martinodes.LatentAVMaskedExtender import LatentAVMaskedExtender
from .martinodes.LatentAVLoadSave import NonePlugger, SaveAVLatent, LoadAVLatent
from .martinodes.LatentOverlappingConcatenator import LatentOverlappingConcatenator, LatentFolderOverlappingConcatenator
from .martinodes.LatentAVCombiner import LatentAVCombiner
from .martinodes.LatentAVSplitter import LatentAVSplitter
from .martinodes.LatentAVContrast import LatentAVContrast
from .martinodes.VideoLatentPicker import VideoLatentPicker
from .martinodes.LatentAVSlicer import LatentAVSlicer
from .martinodes.MinimaxH3KeyframeConditioningInjector import MinimaxH3KeyframeConditioningInjector
from .martinodes.BatchRandomPicker import BatchRandomPicker
from .martinodes.BatchBoundPicker import BatchBoundPicker
from .martinodes.FileLister import FileLister

NODE_CLASS_MAPPINGS = {
    "MARMediaSlicer": MediaSlicer,
    "MARAudioResampler": AudioResampler,
    "MARAudioTrimExtender": AudioTrimExtender,
    "MARAudioInfo": AudioInfo,
    "MARAudioLoader": AudioLoader,
    "MARAudioSilenceSplitter": AudioSilenceSplitter,
    "MARAudioIterator": AudioIterator,
    "MARMediaOverlappingConcatenator": MediaOverlappingConcatenator,
    "MARLatentAVMaskedExtender": LatentAVMaskedExtender,
    "MARLatentAVInfo": LatentAVInfo,
    "MARNonePlugger": NonePlugger,
    "MARSaveAVLatent": SaveAVLatent,
    "MARLoadAVLatent": LoadAVLatent,
    "MARLatentOverlappingConcatenator": LatentOverlappingConcatenator,
    "MARLatentFolderOverlappingConcatenator": LatentFolderOverlappingConcatenator,
    "MARLatentAVCombiner": LatentAVCombiner,
    "MARLatentAVSplitter": LatentAVSplitter,
    "MARLatentAVContrast": LatentAVContrast,
    "MARVideoLatentPicker": VideoLatentPicker,
    "MARLatentAVSlicer": LatentAVSlicer,
    "MARMinimaxH3KeyframeConditioningInjector": MinimaxH3KeyframeConditioningInjector,
    "MARBatchRandomPicker": BatchRandomPicker,
    "MARBatchBoundPicker": BatchBoundPicker,
    "MARFileLister": FileLister
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MARMediaSlicer": "Media head or tail",
    "MARAudioInfo": "Audio info",
    "MARAudioLoader": "Load audio from path",
    "MARAudioSilenceSplitter": "Split audio at silences",
    "MARAudioIterator": "Iterate audio slices",
    "MARAudioResampler": "Resample audio",
    "MARAudioTrimExtender": "Ensure audio duration",
    "MARLatentAVInfo": "Video+audio latent info",
    "MARMediaOverlappingConcatenator": "Concatenate media",
    "MARLatentAVMaskedExtender": "Extend video+audio latent",
    "MARNonePlugger": "None plug",
    "MARSaveAVLatent": "Save video+audio latent",
    "MARLoadAVLatent": "Load video+audio latent",
    "MARLatentOverlappingConcatenator": "Concatenate video+audio latents",
    "MARLatentFolderOverlappingConcatenator": "Concatenate video+audio latents from folder",
    "MARLatentAVCombiner": "Combine video+audio latent",
    "MARLatentAVSplitter": "Split video+audio latent",
    "MARLatentAVContrast": "Adjust video latent contrast",
    "MARVideoLatentPicker": "Pick latent from video",
    "MARLatentAVSlicer": "Slice video+audio latent",
    "MARMinimaxH3KeyframeConditioningInjector": "Inject FL frames into H3 conditioning",
    "MARBatchRandomPicker": "Pick random batch item",
    "MARBatchBoundPicker": "Pick first or last batch item",
    "MARFileLister": "List files in folder"
}