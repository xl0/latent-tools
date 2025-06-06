import random
import sys

def create_float_step_class(step_value):
    """Dynamically create a float step class with the given step value"""
    # Convert step value to a string representation for the class name
    # Remove the decimal point and leading zeros
    step_str = str(step_value).rstrip('0').rstrip('.') if '.' in str(step_value) else str(step_value)
    class_name = f"LTFloat_Step_{step_str.replace('.', '')}"

    # Create the class dynamically
    cls_dict = {
        "CATEGORY": "LatentTools",
        "DESCRIPTION": f"Use as incrementing input that increments by {step_value}",
        "FUNCTION": "value",
        "RETURN_TYPES": ("FLOAT","STRING"),
    }

    # Add the INPUT_TYPES classmethod
    def input_types(cls):
        return {
            "required": {
                "value": ("FLOAT", {"default": 0.0, "min": -1000000, "max": 1000000, "step": step_value}),
            }
        }
    cls_dict["INPUT_TYPES"] = classmethod(input_types)

    # Add the value method
    def value(self, value):
        return (round(value, 5), str(round(value, 5)))
    cls_dict["value"] = value

    # Create the class
    return type(class_name, (), cls_dict)

# Define the step values we want to create classes for
FLOAT_STEP_VALUES = [
    0.0001, 0.0002, 0.0005,  # Very fine steps
    0.001, 0.002, 0.005,     # Fine steps
    0.01, 0.02, 0.05,        # Medium steps
    0.1, 0.2, 0.5,           # Larger steps
    1.0                      # Integer step
]

LTFloatSteps = [ create_float_step_class(step_value) for step_value in FLOAT_STEP_VALUES ]



class LTNumberRangeUniform:
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


class LTNumberRangeGaussian:
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
