import numpy as np
import cv2 as cv
from arbfls.config import config_dict
from arbfls.utils import *


def show_proccess(org_coords, found_coords, side, result_left, result_right, color_left, color_right, config = config_dict,
                  pp_left = None, pp_right = None):
    if side == 'left':
        contoured_org = contour_block(color_left, (245, 121, 5), org_coords, config)
        contoured_org = contour_search_window(contoured_org, (245, 121, 5), org_coords, config)
        contoured_found = contour_block(color_right, (245, 121, 5), found_coords, config)

        cont_pp_left = None
        cont_pp_right = None
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
        cont_pp_left = None
        cont_pp_right = None
        cv.imshow("Esquerda", contoured_found)
        cv.imshow("Direita",contoured_org)
        cv.imshow("Esquerda reconstruida", result_right)
        if pp_left is not None and pp_right is not None:
            cont_pp_left = contour_block(np.clip(pp_left, 0, 255).astype(np.uint8), 128, found_coords, config)
            cont_pp_right = contour_block(np.clip(pp_right, 0, 255).astype(np.uint8), 128, org_coords, config)
            cv.imshow("Esquerda processada", cont_pp_left)
            cv.imshow("Direita processada", cont_pp_right)
        cv.waitKey(0)

