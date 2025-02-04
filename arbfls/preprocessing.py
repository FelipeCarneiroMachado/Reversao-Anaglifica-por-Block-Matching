#Contain the edge detection algorithms
import time

import numpy as np
import cv2 as cv
import imageio as iio
from arbfls.config import config_dict
import arbfls.utils as utils



"""
Deteccao de bordas de marr-hildereth, retorna tanto o Laplaciano da Gaussiana, quanto a imagem de bordas
Creditos a: Adeel Ahmad, disponivel em https://github.com/adl1995/edge-detectors/blob/master/marr-hildreth-edge.py
Usada como opcao de pre-processamento, apresentando melhores resultados
Parametros:
- img: a imagem 
- sigma: ddesvio padrao do filtro gaussiano
Retorno:
- tuple(laplaciano da gaussiana, imagem de bordas)
"""
def edgesMarrHildreth(img, sigma):

    size = int(2*(np.ceil(3*sigma))+1)

    x, y = np.meshgrid(np.arange(-size/2+1, size/2+1),
                       np.arange(-size/2+1, size/2+1))

    normal = 1 / (2.0 * np.pi * sigma**2)

    kernel = ((x**2 + y**2 - (2.0*sigma**2)) / sigma**4) * \
        np.exp(-(x**2+y**2) / (2.0*sigma**2)) / normal  # LoG filter

    kern_size = kernel.shape[0]
    log = np.zeros_like(img, dtype=float)

    # applying filter
    for i in range(img.shape[0]-(kern_size-1)):
        for j in range(img.shape[1]-(kern_size-1)):
            window = img[i:i+kern_size, j:j+kern_size] * kernel
            log[i, j] = np.sum(window)

    log = log.astype(np.int64, copy=False)

    zero_crossing = np.zeros_like(log)

    # computing zero crossing
    for i in range(log.shape[0]-(kern_size-1)):
        for j in range(log.shape[1]-(kern_size-1)):
            if log[i][j] == 0:
                if (log[i][j-1] < 0 and log[i][j+1] > 0) or (log[i][j-1] < 0 and log[i][j+1] < 0) or (log[i-1][j] < 0 and log[i+1][j] > 0) or (log[i-1][j] > 0 and log[i+1][j] < 0):
                    zero_crossing[i][j] = 255
            if log[i][j] < 0:
                if (log[i][j-1] > 0) or (log[i][j+1] > 0) or (log[i-1][j] > 0) or (log[i+1][j] > 0):
                    zero_crossing[i][j] = 255

    return log, zero_crossing

"""
Computa gradientes de sobel de uma imagem, opcao de pre-processamento com resultados inferiores
Parametros:
- img: a imagem 
- mode: o que deve ser retornada
    x -> derivada em funcao de x
    y -> derivada em funcao de y
    l1 -> |dx| + |dy| (aproximacao da norma eucliddiana do gradiente, mais rapido)
    l2 -> sqrt(dx^2 + dy^2) (calculo da norma euclidiana do gradiente, mais lento)
    ang -> arctan(dy/dx),  angulo do vetor gradiente
Retorno:
    matriz/imagem processada
"""
def sobel_wrap(img:np.ndarray, mode):
    gray = cv.cvtColor(img, cv.COLOR_RGB2GRAY)
    gray = cv.GaussianBlur(gray, (7, 7), 0)
    dx, dy = cv.spatialGradient(gray)

    match mode:
        case "x":
            return dx
        case "y":
            return dy
        case "l1":
            return np.abs(dx) + np.abs(dy)
        case "l2":
            return np.sqrt(dx**2 + dy**2)
        case "ang":
            return np.arctan2(dy, dx)
        case _:
            raise NotImplementedError

"""
Aplica o pre processamento especificado pelas configuracoes
Parameters
- l: canal esquerdo
- r: canal direito
- config: dicionario de configuracao, por padrao, config.config_dict
Retorno:
    tuple(esquerda processada, direita processada)
"""
def applyPreProcessing(l:np.ndarray, r:np.ndarray, config:dict =  config_dict)->tuple[np.ndarray]:
    match config["pre_processing"]:
        case "laplacian":
            return (
                edgesMarrHildreth(cv.cvtColor(l, cv.COLOR_RGB2GRAY), config["mh_sigma"])[0], 
                edgesMarrHildreth(cv.cvtColor(r, cv.COLOR_RGB2GRAY), config["mh_sigma"])[0]
            )
        case "abs_laplacian":
            return (
                np.abs(edgesMarrHildreth(cv.cvtColor(l, cv.COLOR_RGB2GRAY), config["mh_sigma"])[0]), 
                np.abs(edgesMarrHildreth(cv.cvtColor(r, cv.COLOR_RGB2GRAY), config["mh_sigma"])[0])
            )
        case "canny":
            params =  config["canny_parameters"]
            return (
                cv.Canny(l, params[0], params[1], apertureSize=params[2], L2gradient=params[3]).astype(np.int32),
                cv.Canny(r, params[0], params[1], apertureSize=params[2], L2gradient=params[3]).astype(np.int32)
            )
        case "marr_hildereth":
            return (edgesMarrHildreth(cv.cvtColor(l, cv.COLOR_RGB2GRAY), config["mh_sigma"])[1].astype(np.int32), 
                    edgesMarrHildreth(cv.cvtColor(r, cv.COLOR_RGB2GRAY), config["mh_sigma"])[1].astype(np.int32))
        case "sobel_x":
            return (
                sobel_wrap(l, "x"),
                sobel_wrap(r, "x")
            )
        case "sobel_y":
            return (
                sobel_wrap(l, "y"),
                sobel_wrap(r, "y")
            )
        case "sobel_l1":
            return (
                sobel_wrap(l, "l1"),
                sobel_wrap(r, "l1")
            )
        case "sobel_l2":
            return (
                sobel_wrap(l, "l2"),
                sobel_wrap(r, "l2")
            )
        case "sobel_ang":
            return (
                sobel_wrap(l, "ang"),
                sobel_wrap(r, "ang")
            )
        case _:
            raise Exception("Unsupported preprocessing")
