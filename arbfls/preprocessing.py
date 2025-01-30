#Contain the edge detection algorithms
import numpy as np
import cv2 as cv
import imageio as iio
from arbfls.config import config_dict
import arbfls.utils as utils




def edgesMarrHildreth(img, sigma):
    """
            finds the edges using MarrHildreth edge detection method...
            :param im : input image
            :param sigma : sigma is the std-deviation and refers to the spread of gaussian
            :return:
            a binary edge image...
    """
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


def sobel_wrap(img:np.ndarray):
    src = cv.GaussianBlur(img, (3, 3), 0)
    gray = cv.cvtColor(src, cv.COLOR_RGB2GRAY)
    scale = 1
    delta = 0
    ddepth = cv.CV_16S

    grad_x = cv.Sobel(gray, ddepth, 1, 0, scale=scale, delta=delta, borderType=cv.BORDER_DEFAULT)
    grad_y = cv.Sobel(gray, ddepth, 0, 1, scale=scale, delta=delta, borderType=cv.BORDER_DEFAULT)


    module_aprox = np.abs(grad_x) + np.abs(grad_y)

    absx = np.abs(grad_x)
    absy = np.abs(grad_y)


    module = np.sqrt(np.square(grad_x.astype(np.int64)) + np.square(absy.astype(np.int64)))


    return grad_x

    


def makeEdgeImages(l:np.ndarray, r:np.ndarray, config:dict =  config_dict)->tuple[np.ndarray]:
    match config["pre_processing"]:
        case "laplacian":
            return (
                edgesMarrHildreth(cv.cvtColor(l, cv.COLOR_RGB2GRAY), config["mh_sigma"])[0], 
                edgesMarrHildreth(cv.cvtColor(r, cv.COLOR_RGB2GRAY), config["mh_sigma"])[0]
            )
        case "abs_laplacian":
            print("Warning: Absolute laplacian edge detection has shown worse results than the laplacian.")
            print("Be sure you are using the correct configuration")
            return (
                np.abs(edgesMarrHildreth(cv.cvtColor(l, cv.COLOR_RGB2GRAY), config["mh_sigma"])[0]), 
                np.abs(edgesMarrHildreth(cv.cvtColor(r, cv.COLOR_RGB2GRAY), config["mh_sigma"])[0])
            )
        case "canny":
            print("Warning: Canny edge detection has shown worse results than the laplacian.")
            print("Be sure you are using the correct configuration")
            params =  config["canny_parameters"]
            return (
                cv.Canny(l, params[0], params[1], apertureSize=params[2], L2gradient=params[3]).astype(np.int32),
                cv.Canny(r, params[0], params[1], apertureSize=params[2], L2gradient=params[3]).astype(np.int32)
            )
        case "marr_hildereth":
            print("Warning: Marr Hildereth edge detection has shown worse results than the laplacian in wich it is based.")
            print("Be sure you are using the correct configuration")
            return (edgesMarrHildreth(cv.cvtColor(l, cv.COLOR_RGB2GRAY), config["mh_sigma"])[1].astype(np.int32), 
                    edgesMarrHildreth(cv.cvtColor(r, cv.COLOR_RGB2GRAY), config["mh_sigma"])[1].astype(np.int32))
        case "sobel":
            # One more failed attempt
            return (
                sobel_wrap(l),
                sobel_wrap(r)
            )
        case _:
            raise Exception("Unsupported preprocessing")
