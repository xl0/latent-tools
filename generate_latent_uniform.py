import torch

class LTRandomUniform:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "channels": ("INT", {"default": 4}),
                "width": ("INT", {"default": 1024}),
                "height": ("INT", {"default": 1024}),
                "batch_size": ("INT", {"default": 1, "min": 1}),
                "min": ("FLOAT", {"default": -1, "min": -1000, "max": 1000, "step": 0.0001}),
                "max": ("FLOAT", {"default": 1, "min": -1000, "max": 1000, "step": 0.0001}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff,
                    "control_after_generate": True,
                    "tooltip": "The random seed used for creating the noise."}),
            },
        }

    CATEGORY = "LatentTools"
    DESCRIPTION = "Fill a latent space with uniform random noise between min and max"
    RETURN_TYPES = ("LATENT",)
    FUNCTION = "random_uniform"
    OUTPUT_NODE = True

    def random_uniform(self, channels: int, width: int, height: int, batch_size: int, min: float, max: float, seed: int):
        generator = torch.Generator()
        generator.manual_seed(seed)
        samples = torch.rand(batch_size, channels, width//8, height//8, generator=generator) * (max - min) + min
        return ({"samples": samples},)