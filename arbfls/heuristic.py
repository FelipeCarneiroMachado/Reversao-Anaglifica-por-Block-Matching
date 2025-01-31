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
    *params => {
        "alpha" : number >= 0 (forca da penalizacao e premiacao) 
    } 
-Picos discretos: baseia-se no fato de que a maioria dos matches tem um deslocamento proximo,
    beneficia blocos em um numero fixo de posicoes, escolhidas pela frequencia de matches.
    Aumenta o tempo de execucao pois requer uma passagem anterior do algoritmo para determinar as frequencias
    *params => { 
        "alpha" : numero >= 0 (forca da penalizacao e premiacao da heuristica flat),
        "beta" : numero >= 0 (forca da penalizacao dos picos discretos),
        "npeaks" : numero >= 0 (quantidade de picos a serem considerados)
    }       
"""


"""
Pre processamento para heuristica de picos discretos e janela_dinamica, busca os deslocamentos de bloco mais freqentes
e retorna o histograma
Parametros:
    pre_processed_left: canal esquerdo com pre-processamento aplicado
    pre_processed_right: canal direito com pre-processamento aplicado
    config: dicionario de configuracao, config.config_dict por padrao
Retorno:
    histograma dos deslocamentos
"""
def compute_match_histogram(pre_processed_left:np.ndarray, pre_processed_right:np.ndarray,config : dict = config_dict) -> tuple[np.ndarray, np.ndarray]:
    dimensions = pre_processed_left.shape
    # Histograma dos matches realizados, armazena os deslocamentos relativos
    histogram = np.zeros(((2 *config["horizontal_window"]) + 1,))
    # Itera sobre a imagem
    for y in range(0, dimensions[0], config["block_size"]):
        for x in range(0, dimensions[1], config["block_size"]):
            # Realiza o match com heuristica flat
            l_match, r_match =  minimize_sad(pre_processed_left, pre_processed_right, dimensions, y, x, config)
            histogram[l_match[1] - x + config["horizontal_window"]] += 1

    # Transformacao em probabilidades
    histogram = histogram / np.sum(histogram)
    return histogram

"""
Computa a lista de deslocamentos para picos discretos com base no histograma
Parametros:
    histogram: histograma de deslocamentos computado por compute_match_histogram
    config: dicionario de configuracao, config.config_dict por padrao
Retorno:
    lista de deslocamentos
"""
def get_point_list(histogram, config:dict = config_dict) -> list:
    return list(map(lambda x : x - 16,np.argpartition(histogram, -config["heuristic_params"]["npeaks"])[-config["heuristic_params"]["npeaks"]:]))


def discrete_points_inmatch(y:int,x:int, config:dict = config_dict) -> int :
    if x <= 0:
        if x in config["heuristic_variables"]["point_list"]:
            return -config["heuristic_params"]["alpha"] - config["heuristic_params"]["beta"]    
        else:
            return -config["heuristic_params"]["alpha"]
    else:
        return config["heuristic_params"]["alpha"]


def find_window_size(histogram ,config : dict = config_dict):
    dw_param = config["dw_config"] # Encurtar expressoes
    # Itera pelo histograma ate encontrar uma posicao acima de um limiar de significancia
    for i in range(len(histogram)):
        if histogram[i] >= dw_param["threshold"]:
            # Retorna o deslocamento multiplicado por uma folga
            return round((config["horizontal_window"] - i) * dw_param["extension"])
    # Nao deve chegar ate esta linha
    return config["horizontal_window"]



def preprocess(edge_left:np.ndarray, edge_right:np.ndarray, config : dict = config_dict, **kwargs) -> dict | None:
    if config["dinamic_window"] or config["heuristic"] == "discrete_points":
        hist_config = config.copy()
        hist_config["heuristic"] = "flat"
        hist_config["heuristic_params"]["alpha"] = 1000
        histogram = compute_match_histogram(edge_left, edge_right, hist_config)
        if config["dinamic_window"]:
            config["horizontal_window"] = find_window_size(histogram, config)
        if config["heuristic"] == "discrete_points":
            return {"point_list" : get_point_list(histogram, config)}
    match config["heuristic"]:
        case "flat":
            return None
        case "discrete_points":
            dp_config = config.copy()
            dp_config["heuristic"] = "flat"
            dp_config["heuristic_params"]["alpha"] = 1000
            return {"point_list" : compute_match_histogram(edge_left, edge_right, dp_config)}
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