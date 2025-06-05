from operator import getitem
import torch
from io import BytesIO
import base64
import lovely_tensors as lt

class LTPreviewLatent:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "latent": ("LATENT", {}),
            }
        }

    CATEGORY = "QTools"
    DESCRIPTION = "Preview a latent tensor"
    FUNCTION = "preview"
    OUTPUT_NODE = True
    RETURN_TYPES = ()

    def preview(self, latent: dict):

        assert isinstance(latent, dict), f"Incorrect type for latent: Expected dict, got {type(latent)}"
        samples = latent["samples"]
        assert isinstance(samples, torch.Tensor), f"Incorrect type for latent.samplels: Expected torch.Tensor, got {type(samples)}"

        mask = latent.get("noise_mask", None)

        # lt uses matplotlib. Set non-interactive backend here.
        import matplotlib
        matplotlib.use('Agg')  # Set non-interactive backend

        # Generate SVG plot
        buf = BytesIO()
        lt.plot(samples, center="range").fig.savefig(buf, format='svg', dpi=100, bbox_inches='tight', pad_inches=0.1,)
        svg_data = buf.getvalue().decode('utf-8')

        # Generate image for channels visualization
        buf = BytesIO()
        lt.chans(samples, scale=2).fig.savefig(buf, format='png', dpi=100, bbox_inches='tight', pad_inches=0)
        img_data_url = f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"

        latent_summary = f"""
    <div class="flex gap-2 items-center">Latent:
        <pre>{lt.lovely(samples, depth=2, color=False)}</pre>
    </div>
    <div class="flex gap-2">Image: Batch size:  {samples.shape[0]}  Resolution:  {samples.shape[-1]*8} x {samples.shape[-2]*8}</div>
    """

        latent_plt = f"""
    <div class="flex flex-col gap-1">
        Distribution:
        <div class="comfy-img-preview">
            {svg_data}
        </div>
    </div>
    """

        latent_chans = f"""
    <div class="flex flex-col gap-1"
        Channels:
        <div class="comfy-img-preview">
            <img src="{img_data_url}" >
        </div>
    </div>
    """

        if mask is not None:
            # Generate SVG plot
            buf = BytesIO()
            lt.plot(mask, center="range").fig.savefig(buf, format='svg', dpi=100, bbox_inches='tight', pad_inches=0.1,)
            mask_svg_data = buf.getvalue().decode('utf-8')

            # Generate image for channels visualization
            buf = BytesIO()
            lt.chans(mask, scale=2).fig.savefig(buf, format='png', dpi=100, bbox_inches='tight', pad_inches=0)
            mask_img_data_url = f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"

            mask_summary = f"""
        <div class="flex gap-2 items-center">Latent:
            <pre>{lt.lovely(mask, depth=2, color=False)}</pre>
        </div>
        <div class="flex gap-2">Image: Batch size:  {mask.shape[0]}  Resolution:  {mask.shape[-1]*8} x {mask.shape[-2]*8}</div>
        """

            mask_plt = f"""
        <div class="flex flex-col gap-1">
            Distribution:
            <div class="comfy-img-preview">
                {mask_svg_data}
            </div>
        </div>
        """

            mask_chans = f"""
        <div class="flex flex-col gap-1"
            Channels:
            <div class="comfy-img-preview">
                <img src="{mask_img_data_url}" >
            </div>
        </div>
        """
        else:
            mask_summary = mask_plt = mask_chans = ""

        html = f"""
<div class="flex flex-col gap-0.5">
{latent_summary}
{mask_summary}
{latent_plt}
{mask_plt}
{latent_chans}
{mask_chans}
</div>
"""
        return {"ui": {"html": (html, )}}