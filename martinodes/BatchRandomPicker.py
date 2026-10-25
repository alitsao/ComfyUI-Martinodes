import math
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
                "weights": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("*",)
    RETURN_NAMES = ("selected",)
    FUNCTION = "run"
    CATEGORY = CATEGORY
    DESCRIPTION = "Selects a random batch or list item deterministically using the seed from a NOISE input and optional comma-separated weights."

    def run(self, noise, any_batch, weights):
        noise = noise[0] if isinstance(noise, list) else noise
        weights = weights[0] if isinstance(weights, list) else weights
        any_batch = unwrap_singleton_batch_input(any_batch)
        batch_size = get_batch_size(any_batch)
        if batch_size == 0:
            raise ValueError("Cannot select an item from an empty batch.")

        if weights.strip():
            try:
                item_weights = [float(weight.strip()) for weight in weights.split(",")]
            except ValueError as error:
                raise ValueError("Weights must be comma-separated numbers.") from error

            if len(item_weights) != batch_size:
                raise ValueError(f"Expected {batch_size} weights, got {len(item_weights)}.")
            if any(not math.isfinite(weight) or weight < 0 for weight in item_weights):
                raise ValueError("Weights must be finite, non-negative numbers.")
            if not any(item_weights):
                raise ValueError("At least one weight must be greater than zero.")
        else:
            item_weights = None

        rng = random.Random(noise.seed)
        if item_weights is None:
            index = rng.randrange(batch_size)
        else:
            index = rng.choices(range(batch_size), weights=item_weights, k=1)[0]
        return (select_batch_item(any_batch, index, batch_size),)
