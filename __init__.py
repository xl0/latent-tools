from .load_latent import QLoadLatent
from .schedulers import LinearScheduler
from .model_metadata_preview import PreviewModelMetadata
from .preview_latent import QPreviewLatent
from .generate_latent_gaussian import QGaussianLatent
from .generate_latent_uniform import QUniformLatent

NODE_CLASS_MAPPINGS = {
    "QLoadLatent": QLoadLatent,
    "LinearScheduler": LinearScheduler,
    "PreviewModelMetadata": PreviewModelMetadata,
    "QPreviewLatent": QPreviewLatent,
    "QGaussianLatent": QGaussianLatent,
    "QUniformLatent": QUniformLatent

}

WEB_DIRECTORY="./web/js"
