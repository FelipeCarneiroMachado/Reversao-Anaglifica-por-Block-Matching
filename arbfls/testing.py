import arbfls.utils as utils
from arbfls.config import config_dict
import numpy as np
import imageio.v3 as iio
from arbfls.anagl_reverse import reverse
import cv2 as cv
from arbfls.register import save_run
from time import sleep



def calculate_psnr(img1, img2, max_value=255):
    """"Calculating peak signal-to-noise ratio (PSNR) between two images."""
    mse = np.mean((np.array(img1, dtype=np.float32) - np.array(img2, dtype=np.float32)) ** 2)
    if mse == 0:
        return 100
    return 20 * np.log10(max_value / (np.sqrt(mse)))





class Test:
    def __init__(self, image:str, im_number:tuple[int, int], **kwargs):
        self.config = config_dict.copy()
        for k, v in kwargs.items():
            self.config[k] = v
        self.image : str = image
        self.folder : str = f"./testBase/{image}/"
        self.im_number : tuple[int, int] = im_number
        if image == "tsukuba":
            self.left_image : np.ndarray = iio.imread(f"{self.folder}scene1.row3.col{self.im_number[0]}.ppm")
            self.right_image : np.ndarray = iio.imread(f"{self.folder}scene1.row3.col{self.im_number[1]}.ppm")
        else:
            self.left_image : np.ndarray = iio.imread(f"{self.folder}im{self.im_number[0]}.ppm")
            self.right_image : np.ndarray = iio.imread(f"{self.folder}im{self.im_number[1]}.ppm")
        self.org_dimensions = self.left_image.shape
        self.anaglyph : np.ndarray = utils.gen_anaglyph(self.left_image, self.right_image, self.config)


    def execute(self):
        self.result_left, self.result_right = utils.return_dimensions(
            *reverse(self.anaglyph, self.config),
            self.org_dimensions, 
            self.config
        )
        self.psnr = (calculate_psnr(self.left_image, self.result_left), calculate_psnr(self.right_image, self.result_right))
        self.psnr = tuple(map(lambda x : round(float(x), 2), self.psnr))
        print(f"Executed {self.image} with {self.config["pre_processing"]} and {self.config["heuristic"]} heuristic")
        print(f"Results: {self.psnr[0]:.2f} || {self.psnr[1]:.2f}")


    def show_results(self, anaglyph = False, original = False):
        cvt = lambda m : cv.cvtColor(m, cv.COLOR_RGB2BGR)
        if original:
            cv.imshow("original left", cvt(self.left_image))
            cv.imshow("original right", cvt(self.right_image))
        if anaglyph:
            cv.imshow("original anaglyph", cvt(self.anaglyph))
            cv.imshow("reconstructed anaglyph", cvt(utils.gen_anaglyph(self.result_left, self.result_right, self.config)))
        cv.imshow("result left", cvt(self.result_left))
        cv.imshow("result right", cvt(self.result_right))
        cv.waitKey(0)
        cv.destroyAllWindows()
    
    def save(self, test_name):
        save_run(
            self.image,
            self.im_number,
            self.psnr,
            test_name,
            self.config
        )

    