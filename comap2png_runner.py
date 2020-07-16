import h5py
import numpy as np
from tqdm import trange
import argparse
import ctypes
import time
import PyGnuplot as gp
from matplotlib.pyplot import subplots
import matplotlib.cm as cm
import os

from comap2png import COMAP2PNG

path = "data/"

filenames = []
for filename in os.listdir(path):
    if filename.endswith(".h5"):
        filenames.append(filename)
        
print(filenames)
for filename in filenames:
    pngname = filename[:-3]
    topng = COMAP2PNG(from_commandline=False, filename=path+filename, outname=pngname, outpath=path)
    topng.run()