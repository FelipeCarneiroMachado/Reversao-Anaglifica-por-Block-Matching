#File for the iteration and block matching execution
import numpy as np
import imageio as iio
from arbfls.config import config_dict
import arbfls.utils as utils
import arbfls.heuristic as heuristic
from time import time
import matplotlib.pyplot as plt

matches = []

#Computes the sad between 2 blocks at the given coordinates 
def sad(leftY:int, leftX:int, rightY:int, rightX:int,
        left_channel:np.ndarray, right_channel:np.ndarray, config:dict=config_dict
        ) -> int:
    bs = config["block_size"] #Shortens the expression
    return np.sum(np.abs(left_channel[leftY:leftY+bs, leftX:leftX+bs] - right_channel[rightY:rightY+bs, rightX:rightX+bs]))

#Finds the minimum sad (correspondent blocl)
def minimize_sad(edge_left:np.ndarray, edge_right:np.ndarray, dimensions:np.shape,
                 y:int, x:int, config:dict=config_dict
                 )-> tuple[tuple[int, int], tuple[int, int]]:

        best_sad_l2r = np.inf
        best_coord_l2r = (None, None)
        best_sad_r2l = np.inf
        best_coord_r2l = (None, None)

        for iterX in range(x  - config["horizontal_window"], x  + config["horizontal_window"] + 1):
            for iterY in range(y - config["vertical_window"], y + config["vertical_window"] + 1):
                if utils.valid_block(iterY, iterX, dimensions, config):
                    #left to right
                    cur_sad = sad(y, x, iterY, iterX, edge_left, edge_right) + heuristic.in_match(iterY-y,iterX-x, config)
                    if cur_sad <= best_sad_l2r:
                        best_sad_l2r = cur_sad
                        best_coord_l2r = (iterY, iterX)
                    #right to left
                    cur_sad = sad(iterY, iterX, y, x, edge_left, edge_right) + heuristic.in_match(iterY-y,-iterX+x, config)
                    if cur_sad <= best_sad_r2l:
                        best_sad_r2l = cur_sad
                        best_coord_r2l = (iterY, iterX)
        matches.append(best_sad_l2r)
        matches.append(best_sad_r2l)
        return best_coord_l2r, best_coord_r2l


#Transfer color to the result channels in place                
def color_transfer(org_coord:tuple[int, int], l_coord:tuple[int, int], r_coord:tuple[int, int],
                   left_color:np.ndarray, right_color:np.ndarray,
                   result_left:np.ndarray, result_right:np.ndarray, config:dict = config_dict
                   ) -> None:
    bs = config["block_size"]
    match config["anaglyph_type"]:
        case "green_magenta":
            result_left[org_coord[0]:org_coord[0]+bs, org_coord[1]:org_coord[1]+bs, [0, 2]] = right_color[l_coord[0]:l_coord[0]+bs, l_coord[1]:l_coord[1]+bs, [0, 2]]
            result_right[org_coord[0]:org_coord[0]+bs, org_coord[1]:org_coord[1]+bs, 1] = left_color[r_coord[0]:r_coord[0]+bs, r_coord[1]:r_coord[1]+bs, 1]
        case "blue_yellow":
            result_left[org_coord[0]:org_coord[0]+bs, org_coord[1]:org_coord[1]+bs, 2] = right_color[l_coord[0]:l_coord[0]+bs, l_coord[1]:l_coord[1]+bs, 2]
            result_right[org_coord[0]:org_coord[0]+bs, org_coord[1]:org_coord[1]+bs, [0,1]] = left_color[r_coord[0]:r_coord[0]+bs, r_coord[1]:r_coord[1]+bs, [0,1]]
        case "red_cyan":
            result_left[org_coord[0]:org_coord[0]+bs, org_coord[1]:org_coord[1]+bs, ] = right_color[l_coord[0]:l_coord[0]+bs, l_coord[1]:l_coord[1]+bs, [0, 2]]
            result_right[org_coord[0]:org_coord[0]+bs, org_coord[1]:org_coord[1]+bs, 1] = left_color[r_coord[0]:r_coord[0]+bs, r_coord[1]:r_coord[1]+bs, 1]
        case _:
            pass 
    


#Executes the block matching algorithm, this is the function that shoud be called by the reversion module
def block_matching(color_left:np.ndarray, color_right:np.ndarray,
                   edge_left:np.ndarray, edge_right:np.ndarray, dimensions : np.shape,
                   config:dict=config_dict
                   )->tuple[np.ndarray, np.ndarray]:
    
    time1 = time()
    #Heuristic pre-processing
    config["heuristic_variables"] = heuristic.preprocess(edge_left, edge_right,config)
    time2 = time()
    print(f"Heuristic preprocessing : {time2-time1:.3f}s")
    print(f"New window size: {config["horizontal_window"]}")
    #Result channels
    result_left = color_left.copy()
    result_right = color_right.copy()

    #Block iteration
    time1 = time()
    for y in range(0, dimensions[0], config["block_size"]):
        for x in range(0, dimensions[1], config["block_size"]):
            l_match, r_match =  minimize_sad(edge_left, edge_right, dimensions, y, x, config)
            color_transfer((y, x), l_match, r_match, color_left, color_right, result_left, result_right, config)
    time2 = time()
    print(f"Block Matching and color transfer : {time2 - time1:.3f}s")
    print(f"Media dos SAD dos matches: {np.mean(matches)}, SD : {np.std(matches)}")
    # plt.hist(matches, bins = 10 )
    # plt.show()
    # No postprocessing was implemented yet, but just in case
    # heuristic.postprocessing(config)

    return result_left, result_right
                   