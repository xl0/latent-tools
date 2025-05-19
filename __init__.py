from .load_latent import QLoadLatent, QLoadLatentTimeline
from .concat_latent_batch import QConcatLatentBatch
from .schedulers import QLinearScheduler
# from .model_metadata_preview import PreviewModelMetadata
from .preview_latent import QPreviewLatent
from .generate_latent_gaussian import QGaussianLatent
from .generate_latent_uniform import QUniformLatent
from .samplers import QKSampler, QSamplerCustom, QSamplerEulerAncestral
from .image_size_setter import QImageSizeSetter

# import lovely_tensors as lt; lt.monkey_patch()

NODE_CLASS_MAPPINGS = {
    "QLoadLatent": QLoadLatent,
    "QLoadLatentTimeline": QLoadLatentTimeline,
    "QConcatLatentBatch": QConcatLatentBatch,
    "QLinearScheduler": QLinearScheduler,
    # "PreviewModelMetadata": PreviewModelMetadata,
    "QPreviewLatent": QPreviewLatent,
    "QGaussianLatent": QGaussianLatent,
    "QUniformLatent": QUniformLatent,
    "QKSampler": QKSampler,
    "QSamplerCustom": QSamplerCustom,
    "QSamplerEulerAncestral": QSamplerEulerAncestral,
    "QImageSizeSetter": QImageSizeSetter
}

WEB_DIRECTORY="./web/js"
