
class QImageSizeSetter:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {"min": 8, "max": 1024*10, "default": 1024}),
                "height": ("INT", {"min": 8, "max": 1024*10, "default": 1024}),
            }
        }

    CATEGORY = "QTools"
    FUNCTION = "size"
    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")

    def size(self, width: int, height: int):
        return (width, height)