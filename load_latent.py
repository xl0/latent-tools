import os
import torch
import hashlib
import folder_paths


normalize_options = ["no", "channel", "image"]

class QLoadLatent:
    @classmethod
    def INPUT_TYPES(cls):

        input_dir = folder_paths.get_input_directory()
        files = []
        for root, dirs, fs in os.walk(input_dir):
            for f in fs:
                if f.endswith(".pt") and os.path.isfile(os.path.join(root, f)):
                    rel_path = os.path.relpath(os.path.join(root, f))
                    files.append(rel_path)

        return {
            "required": {
                "file_path": (sorted(files), {"default": "input/latent.pt"}),
                "normalize": (normalize_options, {"default": normalize_options[0]}),
                "rand_sign": ("BOOLEAN", {"default": False}),
                "rand_sign_seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff})

            },
        }

    CATEGORY = "QTools"

    RETURN_TYPES = ("LATENT",)
    FUNCTION = "load"
    OUTPUT_NODE = True

    def load(self, file_path, normalize, rand_sign, rand_sign_seed):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist.")

        samples = torch.load(file_path)

        # If it's just a tensor, wrap it as expected by ComfyUI
        if isinstance(samples, dict) and "samples" in samples:
            samples = samples["samples"]
        elif not isinstance(samples, torch.Tensor):
            raise ValueError("Unexpected format in PT file.")

        # Convert fp64 tensors into fp32
        if samples.element_size() > 4: samples = samples.to(torch.float32)

        # The LATENT is supposed to be a batch of latents.
        if len(samples.shape) == 3: samples.unsqueeze_(0)

        if rand_sign:
            generator = torch.Generator().manual_seed(rand_sign_seed)
            # Tensor filled with -1 +1 same shape as input
            signs = (torch.randint(size=samples.shape, device=samples.device, low=0, high=2, generator=generator) * 2 - 1)
            samples = samples * signs

        if normalize != "no":

            # The shape of LATENT is BCHW. Normalize either just the whole latent, or each channel separately,
            # which also normalizes the latent as a whole.
            dims = (-2, -1) if normalize == "channel" else (-3, -2, -1)

            means = torch.mean(samples, dim=dims, keepdim=True)
            stds = torch.std(samples, dim=dims, keepdim=True)
            samples = (samples - means) / stds

        return ({"samples": samples},)

    @classmethod
    def IS_CHANGED(cls, file_path, normalize, rand_sign, rand_sign_seed):
        m = hashlib.sha256()
        with open(file_path, 'rb') as f:
            m.update(f.read())
        return (m.digest().hex(), normalize, rand_sign, rand_sign_seed)

    @classmethod
    def VALIDATE_INPUTS(cls, file_path, normalize, rand_sign, rand_sign_seed):
        if normalize not in normalize_options: return f"Invalid option: {normalize}. Expected one of {normalize_options}"

        if not os.path.exists(file_path):
            return f"Invalid latent file: {file_path}"
        return True


normalize_options = ["no", "channel", "image"]

class QLoadLatentTimeline:
    @classmethod
    def INPUT_TYPES(cls):

        input_dir = folder_paths.get_input_directory()
        files = []
        for root, dirs, fs in os.walk(input_dir):
            for f in fs:
                if f.endswith(".pt") and os.path.isfile(os.path.join(root, f)):
                    rel_path = os.path.relpath(os.path.join(root, f))
                    files.append(rel_path)

        return {
            "required": {
                "file_path": (sorted(files), {"default": "input/latent.pt"}),
                "normalize": (normalize_options, {"default": normalize_options[0]}),
                "rand_sign": ("BOOLEAN", {"default": False}),
                "rand_sign_seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff})
            },
        }

    CATEGORY = "QTools"

    RETURN_TYPES = ("LATENT",)
    FUNCTION = "load"
    OUTPUT_NODE = True

    # LATENT_TIMELINE is similar to LATENT, but has an extra dimension T:
    # BTCHW:
    # B - batch (multiple images)
    # T - time - for sampling the noise at different timesteps
    # C - latent channels
    # H, W - Height and Width


    def load(self, file_path, normalize, rand_sign, rand_sign_seed):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist.")

        samples = torch.load(file_path)

        # If it's just a tensor, wrap it as expected by ComfyUI
        if isinstance(samples, dict) and "samples" in samples:
            samples = samples["samples"]
        elif not isinstance(samples, torch.Tensor):
            raise ValueError("Unexpected format in PT file.")

        # Convert fp64 tensors into fp32
        if samples.element_size() > 4: samples = samples.to(torch.float32)

        # In case we got a single latent, expand the dimension T
        if len(samples.shape) == 3: samples.unsqueeze_(0)

        # If we got a single latent timeline (possibly expanded from a single latent),
        # expand it to a batch of latents.
        if len(samples.shape) == 4: samples.unsqueeze_(0)

        if rand_sign:
            generator = torch.Generator().manual_seed(rand_sign_seed)
            # Tensor filled with -1 +1 same shape as input
            signs = (torch.randint(size=samples.shape, device=samples.device, low=0, high=2, generator=generator) * 2 - 1)
            samples = samples * signs

        if normalize != "no":
            # The shape of LATENT is BCHW. Normalize either just the whole latent, or each channel separately,
            # which also normalizes the latent as a whole.
            dims = (-2, -1) if normalize == "channel" else (-3, -2, -1)

            means = torch.mean(samples, dim=dims, keepdim=True)
            stds = torch.std(samples, dim=dims, keepdim=True)
            samples = (samples - means) / stds

        return ({"samples": samples},)

    @classmethod
    def IS_CHANGED(cls, file_path, normalize, rand_sign, rand_sign_seed):
        m = hashlib.sha256()
        with open(file_path, 'rb') as f:
            m.update(f.read())
        return (m.digest().hex(), normalize, rand_sign, rand_sign_seed)

    @classmethod
    def VALIDATE_INPUTS(cls, file_path, normalize, rand_sign, rand_sign_seed):
        if normalize not in normalize_options: return f"Invalid option: {normalize}. Expected one of {normalize_options}"

        if not os.path.exists(file_path):
            return f"Invalid latent file: {file_path}"
        return True
