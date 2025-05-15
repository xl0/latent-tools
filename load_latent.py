import os
import torch
import comfy.utils
import hashlib
from io import BytesIO
from PIL import Image
import numpy as np
import base64

import lovely_tensors as lt

normalize_options = ["no", "channel", "image"]

class QLoadLatent:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_path": ("STRING", {"default": "input/latent.pt"}),
            },
            "optional": {
                "normalize": (normalize_options, {"default": normalize_options[0]})
            }
        }

    CATEGORY = "QTools"

    RETURN_TYPES = ("LATENT",)
    FUNCTION = "load"
    OUTPUT_NODE = True

    def load(self, file_path, normalize):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist.")

        samples = torch.load(file_path, map_location="cpu")

        # If it's just a tensor, wrap it as expected by ComfyUI
        if isinstance(samples, dict) and "samples" in samples:
            samples = samples["samples"]
        elif not isinstance(samples, torch.Tensor):
            raise ValueError("Unexpected format in PT file.")

        # Convert fp64 tensors into fp32
        if samples.element_size() > 4: samples = samples.to(torch.float32)

        # The LATENT is supposed to be a batch of latents.
        if len(samples.shape) == 3: samples.unsqueeze_(0)

        if normalize != "no":

            # The shape of LATENT is BCHW. Normalize either just the whole latent, or each channel separately,
            # which also normalizes the latent as a whole.
            dims = (-2, -1) if normalize == "channel" else (-3, -2, -1)

            means = torch.mean(samples, dim=dims, keepdim=True)
            stds = torch.std(samples, dim=dims, keepdim=True)
            samples = (samples - means) / stds

        return ({"samples": samples},)

    @classmethod
    def IS_CHANGED(cls, file_path, normalize):
        m = hashlib.sha256()
        with open(file_path, 'rb') as f:
            m.update(f.read())
        return (m.digest().hex(), normalize)

    @classmethod
    def VALIDATE_INPUTS(cls, file_path, normalize):
        if normalize not in normalize_options: return f"Invalid option: {normalize}. Expected one of {normalize_options}"

        if not os.path.exists(file_path):
            return f"Invalid latent file: {file_path}"
        return True
