import h5py
# import numpy as np
# import time

f = h5py.File("co6_good_map.h5", "r")
x = f["map"][:,:,1,:,:]
y = f["rms"][:,:,1,:,:]
z = f["nhit"][:,:,1,:,:]

x = f["map"][()]
y = f["rms"][()]
z = f["nhit"][()]
