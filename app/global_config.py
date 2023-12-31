simulations_config = {
    "dice_enabled" : False,
    "monty_hall_enabled" : False,
    "choice_enabled" : False,
    "anti_choice_enabled" : False
}

import random
import numpy as np

def sample_and_sum():
    return sum(random.choices(range(1, 101), k=6))

# Number of times to repeat the sampling
NUM_SAMPLES = 1000000

# List to hold the sum of each sample
SUMS = [sample_and_sum() for _ in range(NUM_SAMPLES)]
MEAN = np.mean(SUMS)
STD = np.std(SUMS)