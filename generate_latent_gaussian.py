import torch

class LTRandomGaussian:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "channels": ("INT", {"default": 4}),
                "width": ("INT", {"default": 1024}),
                "height": ("INT", {"default": 1024}),
                "batch_size": ("INT", {"default": 1}),
                "mean": ("FLOAT", {"default": 0. , "min": -100, "max": 100, "step": 0.0001 }),
                "std": ("FLOAT", {"default": 1. , "min": 0, "max": 100, "step": 0.0001}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff,
                                "control_after_generate": True,
                                "tooltip": "The random seed used for creating the noise."}),
            },
        }

    CATEGORY = "LatentTools"
    DESCRIPTION = "Fill a latent space with gaussian random noise with given mean/std"
    RETURN_TYPES = ("LATENT",)
    FUNCTION = "random_gaussian"
    OUTPUT_NODE = True

    def random_gaussian(self, channels: int, width: int, height: int, batch_size: int, mean: float, std: float, seed: int):
        generator = torch.Generator()
        generator.manual_seed(seed)

        samples = torch.randn(batch_size, channels, height//8, width//8, generator=generator) * std + mean

        return ({"samples": samples},)