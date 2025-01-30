#Main file for the reversion technique
import numpy as np
import imageio as iio
from arbfls.config import config_dict
import arbfls.utils as utils
from arbfls.preprocessing import makeEdgeImages
from arbfls.block_match import block_matching
from time import time
import matplotlib.pyplot as plt


def reverse(anaglyph : np.ndarray, config : dict = config_dict) -> tuple[np.ndarray, np.ndarray]:
    #Saves the anaglyph original dimensios
    org_dimensions = anaglyph.shape
    
    anaglyph = utils.resize_anaglyph(anaglyph, config)
    dimensions = anaglyph.shape

    time1 = time()
    #Returns the left and right images
    left, right= utils.split_channels(anaglyph, config)


    #Computes the processed images used for the comparison
    l_edge, r_edge = makeEdgeImages(left, right, config)

    # plt.hist(l_edge.flatten(), bins=12)
    # plt.show()
    # Executes the block matching
    result_left, result_right = block_matching(left, right, l_edge, r_edge, dimensions, config)

    # Returns to the original dimensions
    result_left, result_right = utils.return_dimensions(result_left, result_right, org_dimensions, config)

    time2 =  time()
    print(f"Total time elapsed : {time2 - time1:.3f}")


    return result_left, result_right


    