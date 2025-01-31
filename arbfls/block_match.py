#File for the iteration and block matching execution
import numpy as np
import imageio as iio
from arbfls.config import config_dict
import arbfls.utils as utils
from arbfls.heuristic import in_match, preprocess
from time import time
import matplotlib.pyplot as plt
from arbfls.sad import sad, minimize_sad

# Funcoes de iteracao pelos canais do anaglifo, computacao das diferencas, escolha de bloco e transferencia de cor
# As coordenadas das imagens sao expressas por X e Y, Y representando as coordenadas verticais e X, as horizontais
# Em termos de indexacao das imagens, o pixel na coordenada (X, Y) eh acessado por imagem[Y, X] (linhas sao o primeiro eixo no numpy)



# Transefere cor de um canal a outro, dadas as coordenadas encontradas pelo block_matching
# A alteracao ocoore in-place
# Args:
#   org_coord: coordenadas (Y, X) destino da transeferencia
#   l_coord: coordenadas (Y, X) fonte da cor para o canal esquerdo
#   r_coord: coordenadas (Y, X) fonte da cor para o canal direito
#   left_color: canal com as cores da esquerda
#   right_color: canal com as cores da direita
#   result_left: resultado da esquerda, eh modificado in-place
#   result_right: resultado da direita, eh modificado in-place
#   config: dicionario de configuracao, por padrao, config.config_dict
# Retorno:
#   Nao retorna valor
def color_transfer(org_coord:tuple[int, int], l_coord:tuple[int, int], r_coord:tuple[int, int],
                   left_color:np.ndarray, right_color:np.ndarray,
                   result_left:np.ndarray, result_right:np.ndarray, config:dict = config_dict
                   ) -> None:
    bs = config["block_size"] # Encurta as expressoes
    # Transeferncia dos canais baseando-se no tipo do anaglifo
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
    


# Executa o algoritmo Block Mathcing para os canais recebidos
# Args:
#   color_left: canal esquerdo do anaglifo, em cores
#   color_right: canal direito do anaglifo, em cores
#   pre_processed_left: canal esquerdo apos pre-processamento
#   pre_processed_right: canal direito apos pre-processamento
#   dimensions: dimensoes (Y, X) dos canais
#   config: dicionario de configuracao, por padrao, config.config_dict
# Retorno:
#   tupla dos canais esquerdo e direito reconstruidos
def block_matching(color_left:np.ndarray, color_right:np.ndarray,
                   pre_processed_left:np.ndarray, pre_processed_right:np.ndarray, dimensions : np.shape,
                   config:dict=config_dict
                   )->tuple[np.ndarray, np.ndarray]:
    
    pre_heuristic_time = time()
    # Pre_processamento de heuristicas
    config["heuristic_variables"] = preprocess(pre_processed_left, pre_processed_right, config)
    post_heuristic_time = time()
    if config["verbose"]:
        print(f"Pre-processamento de heuristica : {pre_heuristic_time-post_heuristic_time:.3f}s")
        if config["dinamic_window"]:
            print(f"Tamanho da janela encontrado: {config["horizontal_window"]}")

    # Inicializacao dos canais resultado
    result_left = color_left.copy()
    result_right = color_right.copy()

    # Iteracao pela imagem, busca da correspondencia e transferencia de cor
    for y in range(0, dimensions[0], config["block_size"]):
        for x in range(0, dimensions[1], config["block_size"]):
            l_match, r_match = minimize_sad(pre_processed_left, pre_processed_right, dimensions, y, x, config)
            color_transfer((y, x), l_match, r_match, color_left, color_right, result_left, result_right, config)
    return result_left, result_right
                   