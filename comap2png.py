import time
t0 = time.time()
import h5py
import numpy as np
from tqdm import trange
import argparse
import ctypes
t1 = time.time()
print("Imports: %.4f" % (t1-t0))

USE_CTYPES = True
USE_GNUPLOT = True

class COMAP2PNG:
    def __init__(self):
        self.parse_arguments()


    def parse_arguments(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("filename", type=str)
        parser.add_argument("-d", "--detectors", type=str, default="range(1,20)", help="List of detectors(feeds), on format which evals to Python list or iterable, e.g. [1,4,9] or range(2,6).")
        parser.add_argument("-s", "--sidebands", type=str, default="range(1,5)", help="List of sidebands, on format which evals to Python list or iterable, e.g. [1,2] or range(1,3).")
        parser.add_argument("-f", "--frequencies", type=str, default="range(1,65)", help="List of frequencies, on format which evals to Python list or iterable, e.g. [34,36,41] or range(12,44).")
        parser.add_argument("-m", "--maptype", type=str, default="map")
        args = parser.parse_args()
        
        self.filename    = args.filename
        
        self.avail_maps = ["map", "rms", "map_rms", "sim", "rms_sim", "hit", "feed", "var"]
        if args.maptype in self.avail_maps:
            self.maptype = args.maptype
        else:
            raise ValueError("Don't recognize map type %s. Available types are %s" % (args.maptype, str(self.avail_maps)))
        
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
            
        self.indexing = []
        non_continuous = 0
        for item in [self.feeds, self.sidebands, self.frequencies]:
            if (len(item) > 1) and ((item[1:] - item[:-1]) != 1).any():  # If there are gaps in the list.
                non_continuous += 1
                self.indexing.append(item-1)  # Data is 0-indexed, input is 1 indexed. Subtract 1.
            else:
                self.indexing.append(slice(item[0]-1, item[-1]))  # Same as above.
        self.indexing = tuple(self.indexing)  # Tuples are nice for slicing.

        if len(self.feeds) == 19:
            self.all_feeds = True
        else:
            self.all_feeds = False

                
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
        h5file    = h5py.File(self.filename, "r")
        self.nx   = h5file["n_x"][()]
        self.ny   = h5file["n_y"][()]
        self.x    = h5file["x"][()]
        self.y    = h5file["y"][()]
        self.freq = h5file["freq"][()]

        if self.all_feeds:  # If we're reading all feeds, we can use the "beam" dataset.
            self.map_full = h5file["map_beam"][self.indexing[1:]][None,:,:,:,:]  # Beam doesn't contain first index, so skip it,
            self.rms_full = h5file["rms_beam"][self.indexing[1:]][None,:,:,:,:]  # Then add empty feed dim,
            self.hit_full = h5file["nhit_beam"][self.indexing[1:]][None,:,:,:,:] # easier compatability with later code.
            print(self.map_full.shape)
        else:
            self.map_full = h5file["map"][self.indexing]
            self.rms_full = h5file["rms"][self.indexing]
            self.hit_full = h5file["nhit"][self.indexing]

        self.num_feeds, self.num_bands, self.num_freqs, self.nx, self.ny = self.map_full.shape

    
    def make_maps(self):
        
        map_full, rms_full, hit_full = self.map_full, self.rms_full, self.hit_full
        if USE_CTYPES:  # Ctypes implementation (much faster).
            nfeed, nband, nfreq, nx, ny = self.map_full.shape
            map_out = np.zeros((ny,nx), dtype=np.float32)
            rms_out = np.zeros((ny,nx), dtype=np.float32)
            hit_out = np.zeros((ny,nx), dtype=np.int32)
            
            maplib = ctypes.cdll.LoadLibrary("maplib.so.1")  # Load shared library
            float32_array2 = np.ctypeslib.ndpointer(dtype=ctypes.c_float, ndim=2, flags="contiguous")
            float32_array5 = np.ctypeslib.ndpointer(dtype=ctypes.c_float, ndim=5, flags="contiguous")
            int32_array2 = np.ctypeslib.ndpointer(dtype=ctypes.c_int, ndim=2, flags="contiguous")
            int32_array5 = np.ctypeslib.ndpointer(dtype=ctypes.c_int, ndim=5, flags="contiguous")
            maplib.makemaps.argtypes = [float32_array5, float32_array5, int32_array5,
                                        float32_array2, float32_array2, int32_array2,
                                        ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
            maplib.makemaps(map_full, rms_full, hit_full, map_out, rms_out, hit_out, nfeed, nband, nfreq, nx, ny)

        else:  # Pure Numpy version.
            nx, ny = self.nx, self.ny
            inv2_hit_rms_full = np.where(hit_full != 0, np.divide(1.0, rms_full**2, out=np.zeros_like(rms_full), where=rms_full!=0), 0.0)

            map_out = np.nansum(map_full*inv2_hit_rms_full, axis=(0,1,2))
            rms_out = np.nansum(inv2_hit_rms_full, axis=(0,1,2))
            hit_out = np.nansum(hit_full, axis=(0,1,2))

        map_out = map_out/np.where(rms_out==0, np.inf, rms_out)
        rms_out = np.sqrt(1.0/np.where(rms_out==0, np.inf, rms_out))
        
        self.map_out, self.rms_out, self.hit_out = map_out, rms_out, hit_out

    
    def plot_maps(self):
        x_lim, y_lim, color_lim = [None,None], [None,None], [None,None]

        if self.maptype == "map":
            plotdata = self.map_out*1e6
            color_lim[1] = 0.1*np.nanmax(plotdata)
            color_lim[0] = -color_lim[1]
        elif self.maptype == "rms":
            plotdata = self.rms_out
        elif self.maptype == "hit":
            plotdata = self.hit_out
        elif self.maptype == "map_rms":
            plotdata = self.map_out/self.rms_out
        # elif self.maptype == "var":
        #     plotdata = self.var_out
        # elif self.maptype == "feed":
        #     plotdata = self.seedbyfeed_out
        # elif self.maptype == "sim":
        #     plotdata = self.sim_out
        # elif self.maptype == "sim_rms":
        #     plotdata = self.simrms_out
        # plotdata = np.ma.masked_where(self.hit_out < 1, plotdata)
        plotdata[self.hit_out < 1] = np.nan

        x, y = self.x, self.y
        dx = x[1] - x[0]
        x_lim[0] = x[0] - 0.5*dx; x_lim[1] = x[-1] + 0.5*dx
        dy = y[1] - y[0]
        y_lim[0] = y[1] - 0.5*dy; y_lim[1] = y[-1] + 0.5*dy

        if USE_GNUPLOT:
            import PyGnuplot as gp
            
            gp.s(plotdata)
            gp.c('set term png')
            gp.c('set output "%s"' % (self.maptype+".png"))
            
            gp.c('set cbrange [%d:%d]' % (color_lim[0], color_lim[1]))
            gp.c('set size ratio 5.0/9.0')
            gp.c('plot "tmp.dat" matrix using (%f+$1*%f):(%f+$2*%f):3 with image' % (x_lim[0], dx, y_lim[0], dy))

        else:            
            from matplotlib.pyplot import subplots
            import matplotlib.cm as cm
            cm.CMRmap.set_bad('0.8',1) #color of masked elements 
            fig, ax = subplots()
            fig.set_figheight(5)
            fig.set_figwidth(9)
            plot = ax.imshow(plotdata, extent=(x_lim[0],x_lim[1],y_lim[0],y_lim[1]), interpolation='nearest', aspect='equal', cmap=cm.CMRmap, origin='lower', vmin=color_lim[0], vmax=color_lim[1])
            fig.colorbar(plot)
            t00 = time.time()
            fig.savefig("%s.png" % self.maptype)
            t11 = time.time()
            print("savefig: ", t11-t00)

    

# if __name__ == "__main__":
map2png = COMAP2PNG()
map2png.run()