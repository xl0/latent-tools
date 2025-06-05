from .generate_latent_gaussian import LTRandomGaussian
from .generate_latent_uniform import LTRandomUniform
from .load_latent import LTLatentLoad

from .preview_latent import LTPreviewLatent
from .reshape_latent import LTReshapeLatent, LTLatentToShape
from .blend_latent import LTBlendLatent
from .latent_op import LTLatentOp
from .concat_latent import LTLatentsConcatenate

from .samplers import LTKSampler

from .param_randomizer import LTRandomRangeGaussian, LTRandomRangeUniform

NODE_CLASS_MAPPINGS = {
    "LTLatentLoad": LTLatentLoad,
    "LTLatentsConcatenate": LTLatentsConcatenate,
    "LTPreviewLatent": LTPreviewLatent,
    "LTGaussianLatent": LTRandomGaussian,
    "LTUniformLatent": LTRandomUniform,
    "LTKSampler": LTKSampler,
    "LTReshapeLatent": LTReshapeLatent,
    "LTLatentToShape": LTLatentToShape,
    "LTBlendLatent": LTBlendLatent,
    "LTLatentOp": LTLatentOp,
    "LTParamRandomizerRange": LTRandomRangeUniform,
    "LTParamRandomizerGaussian": LTRandomRangeGaussian,
}

WEB_DIRECTORY="./web/js"
