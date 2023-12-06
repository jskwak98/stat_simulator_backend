simulations_config = {
    "dice_enabled" : False,
    "monty_hall_enabled" : False,
    "choice_enabled" : False,
    "anti_choice_enabled" : False
}

import random
import numpy as np

def sample_and_sum():
    return sum(random.sample(range(1, 101), 6))

# Number of times to repeat the sampling
num_samples = 1000000

# List to hold the sum of each sample
SUMS = [sample_and_sum() for _ in range(num_samples)]
MEAN = np.mean(SUMS)
STD = np.mean(SUMS)