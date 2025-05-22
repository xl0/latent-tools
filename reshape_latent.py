import torch
import math

class QReshapeLatent:
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

    CATEGORY = "QTools"

    RETURN_TYPES = ("LATENT",)
    FUNCTION = "reshape"
    OUTPUT_NODE = True

    def reshape(self, input, strict, dim0, dim1, dim2, dim3, dim4, dim5, dim6):
        # Get the input tensor
        samples: torch.Tensor = input["samples"]

        # Filter out dimensions that are 0 (not used)
        dimensions = [dim for dim in [dim0, dim1, dim2, dim3, dim4, dim5, dim6] if dim > 0]

        if not dimensions:
            return input  # No reshaping needed

        # Calculate total elements in input and output
        input_size = samples.numel()
        # Calculate total elements in output tensor
        output_size = math.prod(dimensions)

        # Check if sizes match when strict mode is enabled
        if strict and input_size != output_size:
            raise ValueError(f"Input size {input_size} doesn't match output size {output_size} in strict mode")

        # Reshape the tensor
        reshaped = samples.reshape(-1)  # Flatten first

        # If output is larger than input and not strict, repeat elements
        if output_size > input_size and not strict:
            repeats_needed = (output_size + input_size - 1) // input_size  # Ceiling division
            reshaped = reshaped.repeat(repeats_needed)[:output_size]

        # Reshape to target dimensions
        reshaped = reshaped[:output_size].reshape(dimensions)

        return ({"samples": reshaped},)