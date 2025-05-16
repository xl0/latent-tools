from .load_latent import QLoadLatent
from .schedulers import QLinearScheduler
# from .model_metadata_preview import PreviewModelMetadata
from .preview_latent import QPreviewLatent
from .generate_latent_gaussian import QGaussianLatent
from .generate_latent_uniform import QUniformLatent
from .samplers import QKSampler


NODE_CLASS_MAPPINGS = {
    "QLoadLatent": QLoadLatent,
    "QLinearScheduler": QLinearScheduler,
    # "PreviewModelMetadata": PreviewModelMetadata,
    "QPreviewLatent": QPreviewLatent,
    "QGaussianLatent": QGaussianLatent,
    "QUniformLatent": QUniformLatent,
    "QKSampler": QKSampler
}

WEB_DIRECTORY="./web/js"
