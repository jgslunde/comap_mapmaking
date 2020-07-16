import h5py
import numpy as np
import time
import matplotlib.pyplot as plt
from tqdm import trange
import matplotlib.cm as cm
import time
import argparse

class COMAP2PNG:
    def __init__(self):
        self.parse_arguments()


    def parse_arguments(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("filename", type=str)
        parser.add_argument("-d", "--detectors", type=str, default="range(1,20)", help="List of detectors(feeds), on format which evals to Python list or iterable, e.g. [1,4,9] or range(2,6).")
        parser.add_argument("-s", "--sidebands", type=str, default="range(1,5)", help="List of sidebands, on format which evals to Python list or iterable, e.g. [1,2] or range(1,3).")
        parser.add_argument("-f", "--frequencies", type=str, default="range(1,65)", help="List of frequencies, on format which evals to Python list or iterable, e.g. [34,36,41] or range(12,44).")
        args = parser.parse_args()
        
        self.filename    = args.filename
        
        try:
            self.feeds       = np.array(eval(args.detectors))
            self.sidebands   = np.array(eval(args.sidebands))
            self.frequencies = np.array(eval(args.frequencies))
        except:
            raise ValueError("Could not resolve detectors, sidebands, or frequencies as a Python iterable.")
        
        if (self.feeds < 1).any() or (self.feeds > 19).any():
            raise ValueError("Feeds must be in range 1-19.")
        if (self.sidebands < 1).any() or (self.sidebands > 4).any():
            raise ValueError("Sidebands must be in range 1-4.")
        if (self.frequencies < 1).any() or (self.frequencies > 64).any():
            raise ValueError("Frequencies must be in range 1-64.")
            
        if len(self.sidebands) == 19:
            self.all_feeds = True
        else:
            self.all_feeds = False

        self.indexing = []
        non_continuous = 0
        for item in [self.feeds, self.sidebands, self.frequencies]:
            if (len(item) > 1) and ((item[1:] - item[:-1]) != 1).any():  # If there are gaps in the list.
                non_continuous += 1
                self.indexing.append(item)
            else:
                self.indexing.append(slice(item[0], item[-1]+1))
        self.indexing = tuple(self.indexing)  # Tuples are nice for slicing.
                
        if non_continuous > 1:
            raise ValueError("At most one of detectors, sidebands and frequencies may have gaps in their values (e.g. [2,3,6].)")
        

    def run(self):
        t0 = time.time()
        self.read_h5()
        t1 = time.time()
        self.make_maps()
        t2 = time.time()
        self.plot_maps()
        t3 = time.time()
        print(t1-t0)
        print(t2-t1)
        print(t3-t2)


    def read_h5(self):
        h5file        = h5py.File(self.filename, "r")
        self.nx       = h5file["n_x"][()]
        self.ny       = h5file["n_y"][()]
        self.x        = h5file["x"][()]
        self.y        = h5file["y"][()]

        if self.all_feeds:  # If we're reading all feeds, we can use the "beam" dataset.
            self.map_full = h5file["map_beam"][self.indexing][None,:,:,:,:]  # Add empty feed dim, for 
            self.rms_full = h5file["rms_beam"][self.indexing][None,:,:,:,:]  # easier compatability.
            self.hit_full = h5file["nhit_beam"][self.indexing][None,:,:,:,:]
        else:
            self.map_full = h5file["map"][self.indexing]
            self.rms_full = h5file["rms"][self.indexing]
            self.hit_full = h5file["nhit"][self.indexing]

        self.num_feeds, self.num_bands, self.num_freqs, self.nx, self.ny = self.map_full.shape

    
    def make_maps(self):
        nx, ny = self.nx, self.ny
        map_full, rms_full, hit_full = self.map_full, self.rms_full, self.hit_full
        self.map_out = np.zeros((ny,nx), dtype=np.float)
        self.rms_out = np.zeros((ny,nx), dtype=np.float)
        self.hit_out = np.zeros((ny,nx), dtype=np.float)
    
        inv2_hit_rms_full = np.where(hit_full != 0, np.divide(1.0, rms_full**2, out=np.zeros_like(rms_full), where=rms_full!=0), 0.0)

        map_out = np.nansum(map_full*inv2_hit_rms_full, axis=(0,1,2))
        rms_out = np.nansum(inv2_hit_rms_full, axis=(0,1,2))
        hit_out = np.nansum(hit_full, axis=(0,1,2))

        map_out = map_out/rms_out
        rms_out = np.sqrt(1.0/rms_out)
        # rms_out = np.sqrt(1.0/np.where(rms_out==0, 1.0, rms_out))
        
        self.map_out, self.rms_out, self.hit_out = map_out, rms_out, hit_out

    
    def plot_maps(self):
        x_lim, y_lim, color_lim = [None,None], [None,None], [None,None]
        x, y = self.x, self.y
        dx = x[1] - x[0]
        x_lim[0] = x[0] - 0.5*dx; x_lim[1] = x[-1] + 0.5*dx
        dy = y[1] - y[0]
        y_lim[0] = y[1] - 0.5*dy; y_lim[1] = y[-1] + 0.5*dy

        cmap = cm.CMRmap.set_bad('0.8',1) #color of masked elements 
        data = np.ma.masked_where(self.hit_out < 1, self.rms_out)
        fig, ax = plt.subplots()
        plot = ax.imshow(data*1e6, extent=(x_lim[0],x_lim[1],y_lim[0],y_lim[1]), interpolation='nearest', aspect='equal', cmap=cm.CMRmap, origin='lower', vmin=color_lim[0], vmax=color_lim[1])
        fig.colorbar(plot)
        fig.savefig("rms.png")

        data = np.ma.masked_where(self.hit_out < 1, self.hit_out)
        fig, ax = plt.subplots()
        plot = ax.imshow(data*1e6, extent=(x_lim[0],x_lim[1],y_lim[0],y_lim[1]), interpolation='nearest', aspect='equal', cmap=cm.CMRmap, origin='lower', vmin=color_lim[0], vmax=color_lim[1])
        fig.colorbar(plot)
        fig.savefig("hit.png")

        data = np.ma.masked_where(self.hit_out < 1, self.map_out)
        color_lim[1] = 0.1*np.amax(data)*1e6
        color_lim[0] = -color_lim[1]
        fig, ax = plt.subplots()
        plot = ax.imshow(data*1e6, extent=(x_lim[0],x_lim[1],y_lim[0],y_lim[1]), interpolation='nearest', aspect='equal', cmap=cm.CMRmap, origin='lower', vmin=color_lim[0], vmax=color_lim[1])
        fig.colorbar(plot)
        fig.savefig("map.png")

    
    

if __name__ == "__main__":
    map2png = COMAP2PNG()
    map2png.run()