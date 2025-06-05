import torch
import lovely_tensors as lt

ops = ["add", "mul", "pow", "exp", "abs", "clamp_bottom", "clamp_top", "norm", "mean", "std", "sigmoid", "nop"]

class LTLatentOp:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "latent": ("LATENT", {}),
                "op": (ops, {}),
                "arg": ("FLOAT", {"default":0, "min": -99999., "max": 99999., "step": 0.001, "tooltip": "Ignored for exp, abs, normalize and sigmoid"})
            }
        }

    CATEGORY = "LatentTools"
    DESCRIPTION = "Apply an operation to a latent tensor"
    FUNCTION = "op"
    RETURN_TYPES = ("LATENT", )

    def op(self, latent: dict, op: str, arg: float):
        assert isinstance(latent, dict), "latent must be a dict"
        samples = latent["samples"]

        if op == "add":
            samples = samples + arg
        elif op == "mul":
            samples = samples * arg
        elif op == "pow":
            samples = samples ** arg
        elif op == "exp":
            samples = torch.exp(samples)
        elif op == "abs":
            samples = torch.abs(samples)
        elif op == "clamp_bottom":
            samples = torch.clamp(samples, min=arg)
        elif op == "clamp_top":
            samples = torch.clamp(samples, max=arg)
        elif op == "norm":
            samples = (samples - samples.mean()) / samples.std()
        elif op == "mean":
            samples = samples - samples.mean() + arg
        elif op == "std":
            samples = (samples * arg) / samples.std()
        elif op == "sigmoid":
            samples = torch.sigmoid(samples)
        elif op == "sigmoid":
            samples = torch.sigmoid(samples)
        elif op == "nop":
            pass
        else:
            raise ValueError(f"Unknown operation: {op}")

        return ({"samples": samples},)


