# hdf5
## Compile hdf5 as:
```
g++ test.cpp -o test.o -I/usr/include/hdf5/serial
```

## The location of the include was found using 
```
h5c++ -show
```

# GNUPLOT
## compiling with gnuplot
put the gnuplot-iostream.h into the same dir and run 
```
g++ -std=c++17 -o gnuplotter.o gnuplotter.cpp -lboost_iostreams -lboost_system -lboost_filesystem -O3
```



# map.py thingy
```
time python3 -m cProfile -o plotMaps_new.cprof plotMaps_new.py -f co6_good_map.h5 -o test_jonas -j odde -p rms -c [-6e3,6e3]
```
