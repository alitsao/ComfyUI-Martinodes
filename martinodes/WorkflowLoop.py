from .shared import CATEGORY


class WorkflowLoop:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "repeat": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ()
    FUNCTION = "run"
    OUTPUT_NODE = True
    CATEGORY = CATEGORY

    def run(self, repeat):
        return {"ui": {"repeat": [bool(repeat)]}}
