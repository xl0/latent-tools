import torch
import math

class LTLatentToShape:
    max_dim: int = 7
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input": ("LATENT", {}),
            }
        }

    CATEGORY = "LatentTools"
    DESCRIPTION = "Get the shape of a latent tensor"
    RETURN_TYPES = ("INT",)*max_dim
    RETURN_NAMES = tuple(f"dim" for _ in range(max_dim))
    FUNCTION = "shape"

    def shape(self, input: torch.Tensor):
        shape_list = list(input["samples"].shape)

        if len(shape_list) > self.max_dim: shape_list = shape_list[:self.max_dim]

        while len(shape_list) < self.max_dim: shape_list.insert(0, 0)

        return tuple(shape_list)


class LTReshapeLatent:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input": ("LATENT", {}),
                "strict": ("BOOLEAN", {"default": False, "tooltip": "Don't allow total size mismatch between input and output tensors"}),
                "dim0": ("INT", {"default": 0, "min":0, "max":4096}),
                "dim1": ("INT", {"default": 0, "min":0, "max":4096}),
                "dim2": ("INT", {"default": 0, "min":0, "max":4096}),
                "dim3": ("INT", {"default": 1, "min":0, "max":4096}),
                "dim4": ("INT", {"default": 4, "min":0, "max":4096}),
                "dim5": ("INT", {"default": 128, "min":0, "max":4096}),
                "dim6": ("INT", {"default": 128, "min":0, "max":4096}),
            },
        }

    CATEGORY = "LatentTools"
    DESCRIPTION = "Reshape a latent tensor"
    RETURN_TYPES = ("LATENT",)
    FUNCTION = "reshape"

    def reshape(self, input, strict, dim0, dim1, dim2, dim3, dim4, dim5, dim6):
        samples: torch.Tensor = input["samples"]

        dimensions = [dim for dim in [dim0, dim1, dim2, dim3, dim4, dim5, dim6] if dim > 0]

        input_size = samples.numel()
        output_size = math.prod(dimensions)

        if strict and input_size != output_size:
            raise ValueError(f"Input size {input_size} doesn't match output size {output_size} in strict mode")

        reshaped = samples.reshape(-1)

        # If output is larger than input and not strict, repeat elements
        if output_size > input_size and not strict:
            repeats_needed = (output_size + input_size - 1) // input_size
            reshaped = reshaped.repeat(repeats_needed)[:output_size]

        reshaped = reshaped[:output_size].reshape(dimensions)

        return ({"samples": reshaped},)