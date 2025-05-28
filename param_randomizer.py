import random

class QParamaRandomizerList:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "options": ("STRING", {"default":"option1,option2"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff,
                                "control_after_generate": True}),

            }
        }

    CATEGORY = "QTools"
    FUNCTION = "param_randomizer"
    RETURN_TYPES = ("STRING", "INT", "FLOAT")

    def param_randomizer(self, options:str, seed:int):
        local_random = random.Random(seed)
        option_list = options.split(',')
        result = local_random.choice(option_list).strip()

        try:
            float_value = float(result)
            return result, int(float_value), float_value
        except ValueError:
            return result, 0, 0.0

class QParamRandomizerRange:
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

    CATEGORY = "QTools"
    FUNCTION = "param_randomizer"
    RETURN_TYPES = ("FLOAT", "INT")

    def param_randomizer(self, min_value: float, max_value: float, seed: int):
        local_random = random.Random(seed)
        result = local_random.uniform(min_value, max_value)
        return result, int(result)

