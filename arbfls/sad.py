import numpy as np
from arbfls.heuristic import in_match
import arbfls.utils as utils
from arbfls.config import config_dict
# SAD: Soma das diferenças absolutas. Métrica de comparação entre blocos
# Args:
#     leftY: coordenada Y do canto superior esquerdo na imagem esquerda
#     leftX: coordenada X do canto superior esquerdo na imagem esquerda
#     rightY: coordenada Y do canto superior esquerdo na imagem direita
#     rightX: coordenada X do canto superior esquerdo na imagem direita
#     left_channel: canal esquerdo
#     right_channel: canal direito
#     config: dicionario de configuracao, por padrao, config.config_dict
# Retorno:
#     a metrica, como int
def sad(leftY:int, leftX:int, rightY:int, rightX:int,
        left_channel:np.ndarray, right_channel:np.ndarray, config:dict=config_dict
        ) -> int:
    bs = config["block_size"] # Encurta a expressao
    return np.sum(np.abs(left_channel[leftY:leftY+bs, leftX:leftX+bs] - right_channel[rightY:rightY+bs, rightX:rightX+bs]))

# Busca o bloco correspondente na janela de busca, pela minimizacao da SAD.
# A busca eh realizada em ambos os canais, ou seja, as 2 imagens sao recontruidas ao mesmo tempo
# Args:
#     left_channel: canal esquerdo
#     right_channel: canal direito
#     dimensions: dimensoes das imagens
#     y: coordenada Y do canto superior esquerdo do bloco para o qual esta sendo realizada a busca
#     x: coordenada X do canto superior esquerdo do bloco para o qual esta sendo realizada a busca
#     config: dicionario de configuracao, por padrao, config.config_dict
# Retorno:
#     as coordenadas (Y, X) da correspondencia esquerda para a direita, e as coordenadas (Y, X) da correspondencia direita para esquerda
def minimize_sad(left_channel:np.ndarray, right_channel:np.ndarray, dimensions:np.shape,
                 y:int, x:int, config:dict=config_dict
                 )-> tuple[tuple[int, int], tuple[int, int]]:

        # Inicializacao de variaveis: melhor SAD e melhor coordenada
        best_sad_l2r = np.inf
        best_coord_l2r = (None, None)
        best_sad_r2l = np.inf
        best_coord_r2l = (None, None)

        # Iteracao na janela de busca
        for iterX in range(x  - config["horizontal_window"], x  + config["horizontal_window"] + 1):
            for iterY in range(y - config["vertical_window"], y + config["vertical_window"] + 1):
                if utils.valid_block(iterY, iterX, dimensions, config):
                    # Esquerda para direita
                    cur_sad = sad(y, x, iterY, iterX, left_channel, right_channel) + in_match(iterY - y, iterX - x, config)
                    if cur_sad <= best_sad_l2r:
                        best_sad_l2r = cur_sad
                        best_coord_l2r = (iterY, iterX)
                    # DIreita para esquerda
                    cur_sad = sad(iterY, iterX, y, x, left_channel, right_channel) + in_match(iterY - y, -iterX + x, config)
                    if cur_sad <= best_sad_r2l:
                        best_sad_r2l = cur_sad
                        best_coord_r2l = (iterY, iterX)
        return best_coord_l2r, best_coord_r2l

