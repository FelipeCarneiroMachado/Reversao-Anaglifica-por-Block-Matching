"""Configuration dictionary for the package"""

config_dict = {
    "show" : False, #Flag for interactive mode
    "horizontal_window" : 35, #Search window on x axis
    "vertical_window" : 3, #Search window on y axis
    "block_size"  : 8, #Block size (square)
    "mh_sigma" : 0.6, #Sigma parameter for marr-hildereth
    "canny_parameters" : (1.0, 2.0, 5, True), #Low tresh, High thresh, aperture, L2Gradient for canny (Legacy)
    "pre_processing" : "laplacian", #Edge detection algorithm used (see preprocessing)
    "heuristic" : "flat", #Type of heuristic used
    "heuristic_params" : { #The parameters used for the heuristic, must be adjusted to each type
        "alpha" : 1500,
        "beta" : 900,
        "npeaks" : 5
    },
    "heuristic_variables": { #Returned by the heuristic preprocessing

    },
    "dinamic_window" : False, # Adjust the size of the horiontal window dinamically
    "dw_config" : {
        "threshold" : 0.04,
        "extension" : 1.33
    },
    "anaglyph_type" : "green_magenta",  #green_magenta || red_cyan || blue_yellow
    "verbose" : True
}


# Table name for sql registering of experiments
# WARNING: This parameter can only be set trough this file
table_name = "january_testing"

# Pre processing options
pp_list = ["laplacian", "marr_hildereth", "canny"]

# Heuristic options
h_list = ["none", "flat", "discrete_points"]
"""
params for discrete_points
"heuristic_params" : {
    "alpha" : 1000,
    "beta" : 300,
    "npeaks" : 4
}
"""