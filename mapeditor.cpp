# include <ctype.h>
# include <stdio.h>
# include <stdlib.h>
# include <unistd.h>
# include <string>
# include <vector>
# include <iostream>
# include<cstring>
# include <math.h>
# include "H5Cpp.h"

#ifndef H5_NO_NAMESPACE
    using namespace H5;
#endif

void usage(){
    printf("These are the supported operations:\n");
}

void readMap(){
    int NX = 4;
    int NY = 64;
    
    int RANK_OUT = 2;    
    int data_out[NX][NY];

    
    const H5std_string FILE_NAME("co6_good_map.h5");
    const H5std_string DATASET_NAME( "freq" );
    H5File file( FILE_NAME, H5F_ACC_RDONLY);
    DataSet dataset = file.openDataSet( DATASET_NAME );
    DataSpace dataspace = dataset.getSpace();
    
    int rank = dataspace.getSimpleExtentNdims();
    
    hsize_t dims[2];
    rank = dataspace.getSimpleExtentDims(dims);
    DataSpace mspace(RANK_OUT, dims);
    dataset.read(data_out, PredType::NATIVE_INT, mspace, dataspace );
    for (int i = 0; i < NX; i++){
        for (int j = 0; j < NY; j++){
            std::cout << " " << data_out[i][j] << " ";
        }
        std::cout << std::endl;
    }
}


int main(int argc, char *argv[]){
    int opt;
    std::vector<int> sb_list;
    std::vector<int> freq_list;
    std::vector<int> feed_list;
    int sb;
    int freq;
    int feed;
    int list_input;

    int sim_numb = 0;
    int x_index;
    int y_index;
    int number_of_maps;
    int plot_len;

    char *infile;
    char *outfile;
    std::string plot;
    std::string a;

    bool jupiter = false;
    bool deepx   = false;
    bool deepy   = false;

    double scale = 1;
    double rms_lim = 200000;

    int n;              // Length of char* lists
    opterr = 0;

    while ((opt = getopt(argc, argv, "s:i:p:f:h:d:o:x:y:j:z:w:m:r:l:n:")) != -1)
        switch (opt)
        {
        case 's':
            n = strlen(optarg);
            list_input = atoi(optarg);
            for (int i = n - 1; i >= 0; i--){
                sb = (list_input / (int) pow(10, i)) % 10;
                if (sb == 0){
                    printf("Please provide the number of the side band in 1-base, not 0-base!\n");
                    exit(EXIT_FAILURE);
                }
                else if (sb > 4){
                    printf("There are only four side bands!\n");
                    exit(EXIT_FAILURE);
                }
                sb_list.push_back(sb);
            }    
            break;
        case 'i':
            infile = optarg;
            break;
        case 'p':
            plot = optarg;
            if (plot != "map" && plot != "rms" && 
                plot != "hit" && plot != "map/rms"){
                printf("Make sure one of the valid map modes is chosen; 'map', 'rms', 'hit' or 'map/rms'.\n");
                exit(EXIT_FAILURE);
            }
            break;
        case 'f':
            freq = atoi(optarg);
            if (freq == 0){
                printf("Please provide the number of the frequency channels with 1-base, not 0-base!\n");
                exit(EXIT_FAILURE);
            }
            if (freq > 64){
                printf("There are only 64 frequencies pr. side band!\n");
                exit(EXIT_FAILURE);
            }
            
            break;
        case 'h':
            usage();
            break;
        case 'd':
            feed = atoi(optarg);
            if (feed == 0){
                printf("Please provide the number of the feed/detector with 1-base, not 0-base!\n");
                exit(EXIT_FAILURE);
            }
            if (feed > 20){
                printf("There are only 20 feeds/detectors!\n");
                exit(EXIT_FAILURE);
            }
            break;
        case 'o':
            outfile = optarg;
            break;
        case 'j':
            jupiter == true;
            break;
        case 'z':
            sim_numb = atoi(optarg);
            break;
        case 'w':
            scale = atof(optarg);
            break;
        case 'm':
            rms_lim = atof(optarg);
            break;
        case 'l':
            deepx = true;
            y_index = atoi(optarg) - 1;
            break;
        case 'r':
            deepy = true;
            x_index = atoi(optarg) - 1;
            break;
        case 'n':
            number_of_maps = atoi(optarg);
            if (number_of_maps != 1 && number_of_maps != 2){
                printf("Only operations on one or two input maps are supported!\n");
                exit(EXIT_FAILURE);
            }
            break;
        case '?':
            printf("Unknown option: %c\n", optopt);
        default:
            abort();
        }
readMap();
}

