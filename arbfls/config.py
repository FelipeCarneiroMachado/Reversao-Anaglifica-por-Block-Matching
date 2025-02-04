# Dicionario de configuracao do pacote, estas sao as configracoes padrao
# Para utilizar configuracoes customizadas eh possivel alterar neste arquivo ou passar um dicionario alterado como argumento

config_dict = {
    "interactive" : False, # Flag para modo interativo
    "horizontal_window" : 35, # Tamanho horizontal da janela de busca
    "vertical_window" : 3, # Tamanho vertical da janela de busca
    "block_size"  : 8, # Tamanho do bloco (lado do quadrado)
    "mh_sigma" : 0.6, # Parametro sigma do filtro gaussiano aplicado no pre processamento laplaciano/marr-hildereth
    "canny_parameters" : (1.0, 2.0, 5, True), # Parametros do Detector de Bordas de Canny para pre processamento
    # (limiar inferior, limiar superior, tamanho do kernel gaussiano e uso da norma L2 para o gradiente)
    "pre_processing" : "laplacian", # Algoritmo de pre processamento
    "heuristic" : "flat", # Tipo de heuristica utilizada
    "heuristic_params" : { # Parametros da heuristica, ajustados de acordo com o tipo
        "alpha" : 1500,
        "beta" : 900,
        "npeaks" : 5
    },
    "heuristic_variables": {}, # Retornados pelo pre processamento da heuristica
    "dinamic_window" : False, # Ativa o ajuste automatico da janela de busca
    "dw_config" : { # Configuracoes da busca dinamica da janela
        "threshold" : 0.04,
        "extension" : 1.33
    },
    "anaglyph_type" : "green_magenta",  #green_magenta || red_cyan || blue_yellow (Tipo de anaglifo por cor)
    "verbose" : True # Ativa verbosiddade
}
