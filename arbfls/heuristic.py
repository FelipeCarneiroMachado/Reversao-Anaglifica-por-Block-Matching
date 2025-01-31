import numpy as np
import imageio as iio
from arbfls.config import config_dict
import arbfls.utils as utils
from arbfls.sad import sad, minimize_sad
"""
Heuristicas para complementatr a minimizacao da SAD baseando-se na posicao relativa do bloco
"""



"""
Heuristicas implementadas:
-Flat: assume qe os matches corretos estarao todos para o mesmo lado,
    assim penaliza os que estao para o lado contrario, e premia os que estao para o lado "correto"
    *params => {"alpha" : number >= 0 } forca da penalizacao e premiacao
-Picos discretos: baseia-se no fato de que a maioria dos matches tem um deslocamento proximo,
    beneficia blocos em um numero fixo de posicoes, escolhidas pela frequencia de matches.
    Aumenta o tempo de execucao pois requer uma passagem anterior do algoritmo para determinar as frequencias
    *params => {
            
"""



def discrete_points_preprocess(edge_left:np.ndarray, edge_right:np.ndarray,config : dict = config_dict) -> tuple[np.ndarray, np.ndarray]:
    dimensions = edge_left.shape
    histogram = np.zeros(((2 *config["horizontal_window"]) + 1,))
    for y in range(0, dimensions[0], config["block_size"]):
        for x in range(0, dimensions[1], config["block_size"]):
            l_match, r_match =  minimize_sad(edge_left, edge_right, dimensions, y, x, config)
            histogram[l_match[1] - x + config["horizontal_window"]] += 1
    
    mulist = list(map(lambda x : x - 16,np.argpartition(histogram, -config["heuristic_params"]["npeaks"])[-config["heuristic_params"]["npeaks"]:]))
    histogram = histogram / np.sum(histogram)
    # for i, v in enumerate(histogram):
    #     print(f"{i - config["horizontal_window"]} -> {v:.3f}")
    return mulist, histogram
    
def discrete_points_inmatch(y:int,x:int, config:dict = config_dict) -> int :
    if x <= 0:
        if x in config["heuristic_variables"]["mulist"]:
            return -config["heuristic_params"]["alpha"] - config["heuristic_params"]["beta"]    
        else:
            return -config["heuristic_params"]["alpha"]
    else:
        return config["heuristic_params"]["alpha"]


def find_window_size(edge_left:np.ndarray, edge_right:np.ndarray,config : dict = config_dict):
    dp_config = config.copy()
    dp_config["heuristic"] = "flat"
    dp_config["heuristic_params"]["alpha"] = 1000
    mulist, histogram = discrete_points_preprocess(edge_left, edge_right, dp_config)
    dw_param = config["dw_config"]
    for i in range(len(histogram)):
        if histogram[i] >= dw_param["threshold"]:
            config["horizontal_window"] = round((config["horizontal_window"] - i) * dw_param["extension"])
            break
    return mulist


#Heuristic preprocessing function, the parameters are specified in the heuristic_params disctionary in the config_dict
#Other parameters must be passed via kwargs
def preprocess(edge_left:np.ndarray, edge_right:np.ndarray,config : dict = config_dict, **kwargs) -> dict | None:
    if config["dinamic_window"]:
        mulist = find_window_size(edge_left, edge_right, config)
        if config["heuristic"] == "discrete_points":
            return {"mulist" : mulist}
    match config["heuristic"]:
        case "flat":
            return None
        case "discrete_points":
            dp_config = config.copy()
            dp_config["heuristic"] = "flat"
            dp_config["heuristic_params"]["alpha"] = 1000
            return {"mulist" : discrete_points_preprocess(edge_left, edge_right, dp_config)}
        case "none":
            return None
        case _:
            raise Exception("Unsupported heuristic")


#Function called as the heuristic per se, inside the block matching
def in_match(y:int, x:int, config:dict = config_dict) -> int | float:
    match config["heuristic"]:
        case "flat":
            alpha = config["heuristic_params"]["alpha"]
            return alpha if x >= 0 else -alpha
        case "none":
            return 0
        case "discrete_points":
            return discrete_points_inmatch(y, x, config)
        case _:
            return 0

#Heuristic postprocessing function, the parameters are specified in the heuristic_params disctionary in the config_dict
#Other parameters must be passed via kwargs
def postprocessing(edge_left:np.ndarray, edge_right:np.ndarray,config:dict = config_dict, **kwargs) -> dict  | None:
    match config["heuristic"]:
        case "flat":
            None
        case "none":
            return None
        case "discrete_points":
            return None
        case _:
            raise Exception("Unsupported heuristic")