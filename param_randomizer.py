import random

class LTRandomRangeUniform:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "min_value": ("FLOAT", {"default": 0.0, "min": -1000000, "max": 1000000, "step":0.00001}),
                "max_value": ("FLOAT", {"default": 1.0, "min": -1000000, "max": 1000000, "step":0.00001}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff,
                                 "control_after_generate": True}),
            }
        }

    CATEGORY = "LatentTools"
    DESCRIPTION = "Randomize a parameter using a uniform distribution"
    FUNCTION = "param_range_uniform"
    RETURN_TYPES = ("FLOAT", "INT")

    def param_range_uniform(self, min_value: float, max_value: float, seed: int):
        local_random = random.Random(seed)
        result = local_random.uniform(min_value, max_value)
        return result, int(result)


class LTRandomRangeGaussian:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mean": ("FLOAT", {"default": 0.0, "min": -1000000, "max": 1000000, "step":0.00001}),
                "std": ("FLOAT", {"default": 1.0, "min": 0.00001, "max": 1000000, "step":0.00001}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff,
                                 "control_after_generate": True}),
            }
        }

    CATEGORY = "LatentTools"
    DESCRIPTION = "Randomize a parameter using a gaussian distribution"
    FUNCTION = "param_randomizer"
    RETURN_TYPES = ("FLOAT", "INT")

    def param_randomizer(self, mean: float, std: float, seed: int):
        local_random = random.Random(seed)
        result = local_random.gauss(mean, std)
        return result, int(result)
