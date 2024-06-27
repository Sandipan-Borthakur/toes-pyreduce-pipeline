from pyreduce.configuration import get_configuration_for_instrument
from pyreduce.instruments.common import create_custom_instrument
from pyreduce.reduce import Reducer
from pyreduce.util import start_logging
import numpy as np
import os

# Define the path to support files if possible
# otherwise set them to None
# Obviously they are necessary for their respective steps
bpm_mask = None
wavecal_file = None
bias_file = "TOES-reduced/toes.bias.fits"
flat_file = "TOES-reduced/toes.flat.fits"

# create our custom instrument
instrument = create_custom_instrument(
    "TOES", extension=0
)
# Detector
# Override default values
# those can either be fixed values or refer to FITS header keywords
instrument.info["instrument"] = "TOES"
instrument.info["gain"]       =   1.1
instrument.info["readnoise"]  =   5
instrument.info["prescan_x"]  =   0
instrument.info["prescan_y"]  =   0
instrument.info["overscan_x"] =   0
instrument.info["overscan_y"] =   0
instrument.info["longitude"]  =   "GEO_LONG"
instrument.info["latitude"]   =   "GEO_LAT"
instrument.info["altitude"]   =   "GEO_ELEV"

# For loading the config we specify pyreduce as the source, since this is the default
config = get_configuration_for_instrument("pyreduce", plot=1)
# Define your own configuration
config['wavecal_master']['extraction_width'] = 2
config['wavecal_master']['collapse_function'] = 'sum'
config['wavecal_master']['bias_scaling'] = "number_of_files"
config["orders"]["filter_size"] = 15 # smoothing
config["orders"]["degree"] = 4
config["orders"]["degree_before_merge"] = 2
config["orders"]["noise"] = 4.5
config["orders"]["min_cluster"] = 3000
config["orders"]["min_width"] = 200
config["orders"]["manual"] = False
config["norm_flat"]["oversampling"]      =  8  # Subpixel scale for slit function modelling
config["norm_flat"]["swath_width"]       = 400  # Extraction swath width (columns)
config["science"]["oversampling"]        =   8  # Subpixel scale for slit function modelling
config["science"]["swath_width"]         = 400  # Extraction swath width (columns)
config["science"]["smooth_slitfunction"] =   1. # Smoothing of the slit function
config["science"]["smooth_spectrum"]     =   1.0E-6  # Smoothing in spectral direction
config["science"]["extraction_width"]    =[5,5] # Extraction slit height (rows)
config['science']['bias_scaling'] = "number_of_files"
config['wavecal']['medium'] = 'vac'
config['wavecal']['threshold'] = 900
config['wavecal']['shift_window'] = 0.01
config['wavecal']['correlate_cols'] = True
config['wavecal']['degree'] = [7,7]

# Since we can't find the files ourselves (at least not without defining the criteria we are looking for)
# We need to manually define which files go where
files = { "bias": ["2024-06-21/Bias_0s_20240621_221716-%d.fit"%i for i in np.arange(1,11)],
	    "flat": ["2024-06-21/Flat_5s_20240621_222912-%d.fit"%i for i in np.arange(1,5)],
	 "orders": [flat_file],
	 "science": ["2024-06-21/Vega_Object_25s_20240621_224908-%d.fit"%i for i in np.arange(1,2)],
     "wavecal_master":[ "2024-06-21/Vega_Calibration_30s_20240621_225633-1.fit",
                        "2024-06-21/Vega_Calibration_30s_20240621_225633-2.fit",
                        "2024-06-21/Vega_Calibration_30s_20240621_225633-3.fit",
                        "2024-06-21/Vega_Calibration_30s_20240621_225633-4.fit",
                        "2024-06-21/Vega_Calibration_30s_20240621_225633-5.fit"]
    }

# We define the path to the output directory
output_dir = "TOES-reduced"

# (optional) We need to define the log file
log_file = "TOES-reduced/log_file.txt"
start_logging(log_file)


# Define other parameter for PyReduce
target = ""
night = "2024-05-31"

mode = ""
steps = (
   # "bias",
   # "flat",
   # "orders",
   #"scatter",
   # "norm_flat",
   # "wavecal_master",
    "wavecal",
    "science",
    "continuum",
    "finalize",
)

# Call the PyReduce algorithm
reducer = Reducer(
    files,
    output_dir,
    target,
    instrument,
    mode,
    night,
    config,
)
data = reducer.run_steps(steps=steps)
