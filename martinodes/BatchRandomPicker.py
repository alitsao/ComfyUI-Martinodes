import random
from .shared import get_batch_size, select_batch_item, unwrap_singleton_batch_input, CATEGORY


class BatchRandomPicker:
    INPUT_IS_LIST = True

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "noise": ("NOISE",),
                "any_batch": ("*",),
            }
        }

    RETURN_TYPES = ("*",)
    RETURN_NAMES = ("selected",)
    FUNCTION = "run"
    CATEGORY = CATEGORY
    DESCRIPTION = "Selects a random batch item deterministically using the seed from a NOISE input."

    def run(self, noise, any_batch):
        noise = noise[0] if isinstance(noise, list) else noise
        any_batch = unwrap_singleton_batch_input(any_batch)
        batch_size = get_batch_size(any_batch)
        if batch_size == 0:
            raise ValueError("Cannot select an item from an empty batch.")

        index = random.Random(noise.seed).randrange(batch_size)
        return (select_batch_item(any_batch, index, batch_size),)
