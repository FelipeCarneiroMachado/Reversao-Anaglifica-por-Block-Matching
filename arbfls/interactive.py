import numpy as np
import cv2 as cv
from arbfls.config import config_dict
from arbfls.utils import *

"""
Funcoes para executar o modo interativo do programa, mostrando o passo a passo do algoritmo
"""


"""
Desenha um contorno do bloco na imagem, a alteracao eh feita em uma copia retornada, nao in-place
"""
def contour_block(image : np.ndarray, colour : tuple | int, coordinates : tuple[int, int], config : dict = config_dict) -> np.ndarray:
    image = image.copy()
    dimensions = image.shape[:2]
    for x in range(coordinates[0] -1, coordinates[0] + config["block_size"] + 1):
        if valid_coordinate(x, coordinates[1] - 1, dimensions):
            image[x, coordinates[1] - 1] = colour
        if valid_coordinate(x, coordinates[1] + config["block_size"] + 1, dimensions):
            image[x, coordinates[1] + config["block_size"] + 1] = colour
    for y in range(coordinates[1] -1, coordinates[1] + config["block_size"] + 1):
        if valid_coordinate(coordinates[0] - 1, y, dimensions):
            image[coordinates[0] - 1, y] = colour
        if valid_coordinate(coordinates[0] + config["block_size"] + 1, y, dimensions):
            image[coordinates[0] + config["block_size"] + 1, y] = colour
    return image

"""
Desenha um contorno da janela de busca na imagem, a alteracao eh feita em uma copia retornada, nao in-place
"""
def contour_search_window(image:np.ndarray, colour:tuple | int, coordinates:tuple[int, int], config:dict = config_dict)->np.ndarray:
    image = image.copy()
    dimensions = image.shape[:2]
    for y in range(coordinates[0] - config["vertical_window"] - 1, coordinates[0] + config["block_size"] + config["vertical_window"] + 1):
        if valid_coordinate(y, coordinates[1] - config["horizontal_window"]- 1, dimensions):
            image[y, coordinates[1] - config["horizontal_window"]- 1] = colour
        if valid_coordinate(y, coordinates[1] +  config["horizontal_window"] +config["block_size"] + 1, dimensions):
            image[y, coordinates[1] +  config["horizontal_window"] +config["block_size"] + 1] = colour
    for x in range(coordinates[1] -config["horizontal_window"] - 1, coordinates[1]+config["horizontal_window"] + config["block_size"] + 1):
        if valid_coordinate(coordinates[0] -config["vertical_window"]- 1, x, dimensions):
            image[coordinates[0] -config["vertical_window"]- 1, x] = colour
        if valid_coordinate(coordinates[0] + config["block_size"] +config["vertical_window"]+ 1, x, dimensions):
            image[coordinates[0] + config["block_size"] +config["vertical_window"]+ 1, x] = colour
    return image

"""
Mostra as imagens o estado das imagens recuperadas e as correspondencias feitas entre os canais de cores
a cada passo do algoritmo, teclar qualquer tecla prosseguira para a proxima iteracao
"""
def show_proccess(org_coords, found_coords, side, result_left, result_right, color_left, color_right, config = config_dict,
                  pp_left = None, pp_right = None):
    if side == 'left':
        contoured_org = contour_block(color_left, (245, 121, 5), org_coords, config)
        contoured_org = contour_search_window(contoured_org, (245, 121, 5), org_coords, config)
        contoured_found = contour_block(color_right, (245, 121, 5), found_coords, config)
        cv.imshow("Esquerda", cv.cvtColor(contoured_org, cv.COLOR_RGB2BGR))
        cv.imshow("Direita", cv.cvtColor(contoured_found, cv.COLOR_RGB2BGR))
        cv.imshow("Esquerda reconstruida", cv.cvtColor(result_left, cv.COLOR_RGB2BGR))
        if pp_left is not None and pp_right is not None:
            cont_pp_left = contour_block(np.clip(pp_left, 0, 255).astype(np.uint8), 128, org_coords, config)
            cont_pp_right = contour_block(np.clip(pp_right, 0, 255).astype(np.uint8), 128, found_coords, config)
            cv.imshow("Esquerda processada", cont_pp_left)
            cv.imshow("Direita processada", cont_pp_right)
        cv.waitKey(0)

    else:
        contoured_org = contour_block(color_right, (245, 121, 5), org_coords, config)
        contoured_org = contour_search_window(contoured_org, (245, 121, 5), org_coords, config)
        contoured_found = contour_block(color_left, (245, 121, 5), found_coords, config)
        cv.imshow("Esquerda", contoured_found)
        cv.imshow("Direita",contoured_org)
        cv.imshow("Esquerda reconstruida", result_right)
        if pp_left is not None and pp_right is not None:
            cont_pp_left = contour_block(np.clip(pp_left, 0, 255).astype(np.uint8), 128, found_coords, config)
            cont_pp_right = contour_block(np.clip(pp_right, 0, 255).astype(np.uint8), 128, org_coords, config)
            cv.imshow("Esquerda processada", cont_pp_left)
            cv.imshow("Direita processada", cont_pp_right)
        cv.waitKey(0)

