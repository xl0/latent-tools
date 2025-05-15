import torch

class QUniformLatent:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "channels": ("INT", {"default": 4}),
                "width": ("INT", {"default": 512}),
                "height": ("INT", {"default": 512}),
                "batch_size": ("INT", {"default": 1}),
                "min": ("FLOAT", {"default": -1}),
                "max": ("FLOAT", {"default": 1}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff, "control_after_generate": True, "tooltip": "The random seed used for creating the noise."}),
            },
        }

    CATEGORY = "QTools"

    RETURN_TYPES = ("LATENT",)
    FUNCTION = "random_uniform"
    OUTPUT_NODE = True

    def random_uniform(self, channels: int, width: int, height: int, batch_size: int, min: float, max: float, seed: int):
        generator = torch.Generator()
        generator.manual_seed(seed)
        samples = torch.rand(batch_size, channels, width//8, height//8, generator=generator) * (max - min) + min
        return ({"samples": samples},)

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return kwargs["seed"]

    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        return True
