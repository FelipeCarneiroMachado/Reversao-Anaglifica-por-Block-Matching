import numpy as np
from arbfls.config import config_dict
import arbfls.utils as utils
from arbfls.preprocessing import applyPreProcessing
from arbfls.block_match import block_matching
from time import time


# Função principal da reversão, recebe o anáglifo como array numpy e retorna os 2 canais, tambpem como array numpy
# Args:
#     anaglyph: o anáglifo como array numpy, 3 dimensões, cores RGB
#     config (opcional): dicionario de configuração, caso não especificado, configuração padrão presente em config.py
# Retorno:
#     tupla contendo, respectivamente, as visões esquerda e direita restauradas
def reverse(anaglyph : np.ndarray, config : dict = config_dict) -> tuple[np.ndarray, np.ndarray]:

    if config["verbose"]:
        print("Iniciando reversão anaglífica.")
        print(f"Anáglifo {config["anaglyph_type"]} de dimensões {anaglyph.shape[:2]}")
        print(f"Pré processamento:{config["pre_processing"]}")
        print(f"Heurística:{config["heuristic"]}")

    # Benchmarking
    initial_time = time()

    # Salva as dimensões originais
    org_dimensions = anaglyph.shape

    # Redimensiona o anáglifo para que seja divisível pelo tamanho de bloco
    anaglyph = utils.resize_anaglyph(anaglyph, config)
    dimensions = anaglyph.shape

    resize_time = time()

    if config["verbose"]:
        print(f"Redimensionamento conluído: {resize_time - initial_time:.3f}")

    # Separa os canais esquerdo e direito do anáglifo
    left, right= utils.split_channels(anaglyph, config)

    split_time = time()
    if config["verbose"]:
        print(f"Split concluido: {split_time - resize_time:.3f}")

    # Aplica o pre-processamento às imagens
    l_processed, r_processed = applyPreProcessing(left, right, config)

    pre_processed_time = time()
    if config["verbose"]:
        print(f"Pre-Processameto concluido: {pre_processed_time - split_time:.3f}")

    # Executa o block matching
    result_left, result_right = block_matching(left, right, l_processed, r_processed, dimensions, config)

    match_time = time()
    if config["verbose"]:
        print(f"Match concluido: {match_time - pre_processed_time:.3f}")

    # Retorna às dimensões originais
    result_left, result_right = utils.return_dimensions(result_left, result_right, org_dimensions, config)

    final_time =  time()
    print(f"Tempo total decorrido : {final_time - initial_time:.3f}")


    return result_left, result_right


    