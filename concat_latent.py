import torch

class LTLatentsConcatenate:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "latent1": ("LATENT", {}),
                "latent2": ("LATENT", {}),
                "dim": ("INT", {"min":-10, "max": 10, "default":-4})
            }
        }

    CATEGORY = "LatentTools"
    DESCRIPTION = "Concatenate two latents along a given dimension"
    FUNCTION = "concat"
    RETURN_TYPES = ("LATENT", )

    def concat(self, latent1: dict, latent2: dict, dim:int):
        assert isinstance(latent1, dict), f"Incorrect type for latent1: Expected dict, got {type(latent1)}"
        assert isinstance(latent2, dict), f"Incorrect type for latent2: Expected dict, got {type(latent2)}"
        samples1 = latent1["samples"]
        samples2 = latent2["samples"]
        assert isinstance(samples1, torch.Tensor), f"Incorrect type for latent1.samples: Expected torch.Tensor, got {type(samples1).__name__}"
        assert isinstance(samples2, torch.Tensor), f"Incorrect type for latent2.samples: Expected torch.Tensor, got {type(samples2).__name__}"
        
        # Validate dimensions
        if samples1.dim() != samples2.dim():
            raise ValueError(f"Dimension mismatch: latent1 has {samples1.dim()} dimensions, latent2 has {samples2.dim()} dimensions")

        # The video models have weird number of dimensions. As long as the numbers match, just let it be.
        # if samples1.dim() < 4: raise ValueError(f"latent1 should have 4 dimensions, got {samples1.dim()} dimensions")
        # if samples2.dim() != 4: raise ValueError(f"latent2 should have 4 dimensions, got {samples2.dim()} dimensions")

        concatenated = torch.cat([samples1, samples2], dim=dim)

        return ({"samples": concatenated},)