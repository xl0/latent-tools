import torch

blend_choice = ["interpolate", "add", "multiply", "abs_max", "abs_min", "max", "min", "sample"]

class LTBlendLatent:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "latent1": ("LATENT", {}),
                "latent2": ("LATENT", {}),
                "mode": (blend_choice, {}),
                "ratio": ("FLOAT", {"min": 0, "max":1, "default":0.5, "step": 0.001}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff,
                                "control_after_generate": True,
                                "tooltip": "See of the random sampling (mode=sample"}),
            }
        }

    CATEGORY = "LatentTools"
    DESCRIPTION = "Blend two latent tensors using different modes"
    FUNCTION = "blend"
    RETURN_TYPES = ("LATENT", )

    def blend(self, latent1: dict, latent2: dict, mode: str, ratio:int, seed: int):
        assert isinstance(latent1, dict) and isinstance(latent2, dict), "Inputs must be dictionaries"
        samples1, samples2 = latent1["samples"], latent2["samples"]

        assert isinstance(samples1, torch.Tensor), "latent1['samples'] must be torch.Tensor"
        assert isinstance(samples2, torch.Tensor), "latent2['samples'] must be torch.Tensor"

        assert samples1.shape == samples2.shape, f"Shape mismatch: latent1: {samples1.shape} vs latent2: {samples2.shape}"

        if mode == "interpolate":
            blended = samples1 * ratio + samples2 * (1 - ratio)
        elif mode == "add":
            blended = samples1 + samples2
        elif mode == "multiply":
            blended = samples1 * samples2
        elif mode == "abs_max":
            blended = torch.where(torch.abs(samples1) > torch.abs(samples2), samples1, samples2)
        elif mode == "abs_min":
            blended = torch.where(torch.abs(samples1) < torch.abs(samples2), samples1, samples2)
        elif mode == "max":
            blended = torch.maximum(samples1, samples2)
        elif mode == "min":
            blended = torch.minimum(samples1, samples2)
        elif mode == "sample":
            torch.manual_seed(seed)
            mask = torch.rand_like(samples1) >= ratio
            blended = torch.where(mask, samples1, samples2)
        else:
            raise ValueError(f"Unknown blend mode: {mode}")

        return ({"samples": blended},)


