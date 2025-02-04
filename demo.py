import imageio.v3 as iio
from arbfls.config import config_dict
from arbfls.anagl_reverse import reverse
from arbfls.utils import gen_anaglyph

"""
Demonstracao do algoritmo, com configuracoes padrao e modo interativo
"""


esquerda = iio.imread("demo_images/im1.ppm")
direita = iio.imread("demo_images/im2.ppm")
config = config_dict.copy()
# Modo interativo
config["interactive"] = True
config["verbose"] = True
anaglifo = gen_anaglyph(esquerda, direita, config)

ret = reverse(anaglifo, config)

