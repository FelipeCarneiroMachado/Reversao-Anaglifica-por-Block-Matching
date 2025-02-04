import numpy as np
import cv2 as cv
import imageio as iio
from arbfls.config import config_dict

"""
Utiliadades gerais para o pacote
"""

"""
Separa os canais esquerdo e direitos do anaglifo
"""
def split_channels(anaglyph : np.ndarray, config : dict = config_dict) -> tuple[np.ndarray, np.ndarray]:
    #Split the channels
    match config["anaglyph_type"]:
        case "green_magenta": 
            l = anaglyph.copy()
            l[:, :, 0] = l[:, :, 1]
            l[:, :, 2] = l[:, :, 1]
            r =  anaglyph.copy()
            r[:, :, 1] = r[:, :, 0]
        case "red_cyan":
            l = anaglyph[:, :, 0]
            r =  anaglyph.copy()
            r[:, :, 0] *= 0
        case "blue_yellow":
            l = anaglyph[:, :, 2]
            r =  anaglyph.copy()
            r[:, :, 2] *= 0
        case _:
            raise Exception("Unsuported anaglyph type")
    return l, r
  

"""
Altera as dimensoes do anaglifo de modo a ser divisivel pelo tamanho do bloco, preenchendo as bordas com preto
"""
def resize_anaglyph(anaglyph:np.ndarray, config:dict = config_dict):
    # Funcao para encontrar a nova dimensao
    f = lambda x : (config["block_size"] - (x % config["block_size"])
                    if x % config["block_size"] != 0 
                    else 0)

    resized = cv.copyMakeBorder(anaglyph
                                  , 0,
                                  f(anaglyph.shape[0]),
                                  0,
                                  f(anaglyph.shape[1]),
                                  cv.BORDER_CONSTANT,
                                  value=[0, 0, 0])
    return resized

"""
Altera as dimensoes das imagens de modo a ser divisivel pelo tamanho do bloco, preenchendo as bordas com preto
"""
def resize_channels(l:np.ndarray, r:np.ndarray, config:dict = config_dict)->tuple[np.ndarray,np.ndarray, np.shape]:
    # Funcao para encontrar a nova dimensao
    f = lambda x : (config["block_size"] - (x % config["block_size"]) 
                    if x % config["block_size"] != 0 
                    else 0)

    resized_l = cv.copyMakeBorder(l
                                  , 0,
                                  f(l.shape[0]),
                                  0,
                                  f(l.shape[1]),
                                  cv.BORDER_CONSTANT,
                                  value=[0, 0, 0])
    resized_r = cv.copyMakeBorder(r
                                  , 0,
                                  f(r.shape[0]),
                                  0,
                                  f(r.shape[1]),
                                  cv.BORDER_CONSTANT,
                                  value=[0, 0, 0])
    return resized_l, resized_r, resized_l.shape


"""
Retorna se uma dada coordenada eh um ponto valido da imagem
"""
def valid_coordinate(y:int, x:int, dimensions:tuple[int, int, int])->bool:
    if x >= 0 and x < (dimensions[1]):
        if y >= 0 and y < (dimensions[0]):
            return True
        else:
            return False
    else:
        return False
    
"""
Retorna se uma dada coordenada corresponde a um bloco inteiramente dentro da imagem 
note que o bloco eh representado pelo canto superior esquerdo
"""
def valid_block(y : int, x : int, dimensions:tuple[int, int, int], config : dict = config_dict) -> bool:
    if x >= 0 and x <= (dimensions[1] - config["block_size"]):
        if y >= 0 and y <= (dimensions[0] - config["block_size"]):
            return True
        else:
            return False
    else:
        return False


"""
Retorna os canais as dimensoes originais
"""
def return_dimensions(result_left:np.ndarray, result_right:np.ndarray, dimensions:np.shape, config:dict = config_dict) -> None:
    bs = config["block_size"]
    f = lambda x :  -(bs - (x % bs)) if x % bs != 0 else x
    l = result_left[:dimensions[0], :dimensions[1]]
    r = result_right[:dimensions[0], :dimensions[1]]
    return l, r

"""
Gera uma anaglifo a partir de um par estereo
"""
def gen_anaglyph(l:np.ndarray, r:np.ndarray, config:dict = config_dict) -> np.ndarray:
    match config["anaglyph_type"]:
        case "green_magenta": 
            l, r, d = resize_channels(l, r, config)
            anaglyph = l.copy()
            anaglyph[:, :, [0, 2]] = r[:, :, [0, 2]]
        case "red_cyan":
            l, r, d = resize_channels(l, r, config)
            anaglyph = l.copy()
            anaglyph[:, :, [1, 2]] = r[:, :, [1, 2]]
        case "blue_yellow":
            l, r, d = resize_channels(l, r, config)
            anaglyph = l.copy()
            anaglyph[:, :, [0, 1]] = r[:, :, [0, 1]]
        case _:
            raise Exception("Unsuported anaglyph type")
    return anaglyph

"""
Calcula o psnr entre 2 imagens, metrica objetiva da qualidade de reconstrucao
"""
def calculate_psnr(img1, img2, max_value=255):
    mse = np.mean((np.array(img1, dtype=np.float32) - np.array(img2, dtype=np.float32)) ** 2)
    if mse == 0:
        return 100
    return 20 * np.log10(max_value / (np.sqrt(mse)))


