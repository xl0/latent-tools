from .load_latent import QLoadLatent, QLoadLatentTimeline
from .schedulers import QLinearScheduler
# from .model_metadata_preview import PreviewModelMetadata
from .preview_latent import QPreviewLatent
from .generate_latent_gaussian import QGaussianLatent
from .generate_latent_uniform import QUniformLatent
from .samplers import QKSampler, QSamplerCustom, QSamplerEulerAncestral

import lovely_tensors as lt; lt.monkey_patch()

NODE_CLASS_MAPPINGS = {
    "QLoadLatent": QLoadLatent,
    "QLoadLatentTimeline": QLoadLatentTimeline,
    "QLinearScheduler": QLinearScheduler,
    # "PreviewModelMetadata": PreviewModelMetadata,
    "QPreviewLatent": QPreviewLatent,
    "QGaussianLatent": QGaussianLatent,
    "QUniformLatent": QUniformLatent,
    "QKSampler": QKSampler,
    "QSamplerCustom": QSamplerCustom,
    "QSamplerEulerAncestral": QSamplerEulerAncestral
}

WEB_DIRECTORY="./web/js"
