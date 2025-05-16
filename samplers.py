# Derived from KSampler from ComfyUI nodes.py
# License for this file only: GPL v3

import torch
import numpy as np

import comfy
import comfy.sample
import comfy.utils
import comfy.samplers

import latent_preview


def qprepare_noise(latent_noise, noise_inds=None):

    if noise_inds is None:
        return latent_noise

    unique_inds = np.unique(noise_inds)
    noises = [latent_noise[i:i+1] for i in unique_inds]
    return torch.cat([noises[np.where(unique_inds == i)[0][0]] for i in noise_inds], dim=0)


def common_qksampler(model, latent_noise, extra_seed, steps, cfg, sampler_name, scheduler, positive, negative, latent_image, denoise=1.0, disable_noise=False, start_step=None, last_step=None, force_full_denoise=False):
    latent_image_samples: torch.Tensor = latent_image["samples"]
    latent_noise_samples: torch.Tensor = latent_noise["samples"]
    # latent_image_samples = comfy.sample.fix_empty_latent_channels(model, latent_image_samples)
    assert model.get_model_object("latent_format").latent_channels == latent_image_samples.shape[1], "Wrong number of latent channels"
    assert latent_noise_samples.dim() == latent_image_samples.dim(), "Unexpected number of dimensions"
    assert latent_noise_samples.shape[-3:] == latent_image_samples.shape[-3:], "Shape mismatch"

    if disable_noise:
        noise = torch.zeros_like(latent_image_samples)
    else:
        batch_inds = latent_image["batch_index"] if "batch_index" in latent_image else None
        noise = qprepare_noise(latent_noise_samples, batch_inds)


    # If we have 1 sample of noise, and multiple input images, broadcast the noise to match the input.
    if noise.shape[0] == 1 and latent_image_samples.shape[0] != 1:
        noise = noise.broadcast_to(size=latent_image_samples.shape)

    noise_mask = None
    if "noise_mask" in latent_image:
        noise_mask = latent_image["noise_mask"]

    callback = latent_preview.prepare_callback(model, steps)
    disable_pbar = not comfy.utils.PROGRESS_BAR_ENABLED
    samples = comfy.sample.sample(model, noise, steps, cfg, sampler_name, scheduler, positive, negative, latent_image_samples,
                                  denoise=denoise, disable_noise=disable_noise, start_step=start_step, last_step=last_step,
                                  force_full_denoise=force_full_denoise, noise_mask=noise_mask, callback=callback, disable_pbar=disable_pbar, seed=extra_seed)
    out = latent_image.copy()
    out["samples"] = samples
    return (out, )

class QKSampler:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": ("MODEL", {"tooltip": "The model used for denoising the input latent."}),
                "latent_noise": ("LATENT", {}),
                "extra_seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff, "control_after_generate": True, "tooltip": "The random seed used for creating the noise."}),
                "steps": ("INT", {"default": 20, "min": 1, "max": 10000, "tooltip": "The number of steps used in the denoising process."}),
                "cfg": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0, "step":0.1, "round": 0.01, "tooltip": "The Classifier-Free Guidance scale balances creativity and adherence to the prompt. Higher values result in images more closely matching the prompt however too high values will negatively impact quality."}),
                "sampler_name": (comfy.samplers.KSampler.SAMPLERS, {"tooltip": "The algorithm used when sampling, this can affect the quality, speed, and style of the generated output."}),
                "scheduler": (comfy.samplers.KSampler.SCHEDULERS, {"tooltip": "The scheduler controls how noise is gradually removed to form the image."}),
                "positive": ("CONDITIONING", {"tooltip": "The conditioning describing the attributes you want to include in the image."}),
                "negative": ("CONDITIONING", {"tooltip": "The conditioning describing the attributes you want to exclude from the image."}),
                "latent_image": ("LATENT", {"tooltip": "The latent image to denoise."}),
                "denoise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "The amount of denoising applied, lower values will maintain the structure of the initial image allowing for image to image sampling."}),
            }
        }

    RETURN_TYPES = ("LATENT",)
    OUTPUT_TOOLTIPS = ("The denoised latent.",)
    FUNCTION = "sample"

    CATEGORY = "sampling"
    DESCRIPTION = "Uses the provided model, positive and negative conditioning to denoise the latent image."

    def sample(self, model, latent_noise, extra_seed, steps, cfg, sampler_name, scheduler, positive, negative, latent_image, denoise=1.0):
        return common_qksampler(model, latent_noise, extra_seed, steps, cfg, sampler_name, scheduler, positive, negative, latent_image, denoise=denoise)
