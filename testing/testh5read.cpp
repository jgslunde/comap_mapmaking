#include <iostream>
#include <string>
#include <H5Cpp.h>

using namespace std;
using namespace H5;


const H5std_string FILE_NAME( "co6_good_map.h5" );  // Name of h5 file.
const H5std_string map_name( "map" );  // Name of dataset field.
const H5std_string rms_name( "rms" );  // Name of dataset field.
const H5std_string hit_name( "nhit" );  // Name of dataset field.

const int    NFEED = 19;
const int    NBAND = 4;
const int    NFREQ = 1;
const int    NY = 120;
const int    NX = 120;

const int RANK_OUT = 5;

int main(){
    float *****map = new float****[NFEED];
    for(int i=0; i<NFEED; i++){
        map[i] = new float***[NBAND];
        for(int j=0; j<NBAND; j++){
            map[i][j] = new float**[NFREQ];
            for(int k=0; k<NFREQ; k++){
                map[i][j][k] = new float*[NX];
                for(int l=0; l<NX; l++){
                    map[i][j][k][l] = new float[NY];
                }
            }
        }
    }

    float *****rms = new float****[NFEED];
    for(int i=0; i<NFEED; i++){
        rms[i] = new float***[NBAND];
        for(int j=0; j<NBAND; j++){
            rms[i][j] = new float**[NFREQ];
            for(int k=0; k<NFREQ; k++){
                rms[i][j][k] = new float*[NX];
                for(int l=0; l<NX; l++){
                    rms[i][j][k][l] = new float[NY];
                }
            }
        }
    }

    int *****hit = new int****[NFEED];
    for(int i=0; i<NFEED; i++){
        hit[i] = new int***[NBAND];
        for(int j=0; j<NBAND; j++){
            hit[i][j] = new int**[NFREQ];
            for(int k=0; k<NFREQ; k++){
                hit[i][j][k] = new int*[NX];
                for(int l=0; l<NX; l++){
                    hit[i][j][k][l] = new int[NY];
                }
            }
        }
    }
    // float map[NFEED][NBAND][NFREQ][NX][NY];
    // float rms[NFEED][NBAND][NFREQ][NX][NY];
    // int hit[NFEED][NBAND][NFREQ][NX][NY];
    // float *data_out;
    // data_out = new float[NFEED][NBAND][NFREQ][NX][NY];

    H5File file( FILE_NAME, H5F_ACC_RDONLY );
    DataSet dataset_map = file.openDataSet( map_name );
    DataSet dataset_rms = file.openDataSet( rms_name );
    DataSet dataset_hit = file.openDataSet( hit_name );

    DataSpace dataspace_map = dataset_map.getSpace();
    DataSpace dataspace_rms = dataset_rms.getSpace();
    DataSpace dataspace_hit = dataset_hit.getSpace();
    // int rank = dataspace.getSimpleExtentNdims();

    // hsize_t dims_out[5];
    // int ndims = dataspace.getSimpleExtentDims( dims_out, NULL);
    // cout << "rank " << rank << ", dimensions " <<
    //     (unsigned long)(dims_out[0]) << " x " <<
    //     (unsigned long)(dims_out[1]) << " x " <<
    //     (unsigned long)(dims_out[2]) << " x " <<
    //     (unsigned long)(dims_out[3]) << " x " <<
    //     (unsigned long)(dims_out[4]) << endl;

    hsize_t      offset[5];
    hsize_t      count[5];
    offset[0] = 0;
    offset[1] = 0;
    offset[2] = 0;
    offset[3] = 0;
    offset[4] = 0;
    count[0]  = NFEED;
    count[1]  = NBAND;
    count[2]  = NFREQ;
    count[3]  = NX;
    count[4]  = NY;

    dataspace_map.selectHyperslab( H5S_SELECT_SET, count, offset );
    dataspace_rms.selectHyperslab( H5S_SELECT_SET, count, offset );
    dataspace_hit.selectHyperslab( H5S_SELECT_SET, count, offset );

    // Define the memory dataspace.
    hsize_t dimsm[5];
    dimsm[0] = NFEED;
    dimsm[1] = NBAND;
    dimsm[2] = NFREQ;
    dimsm[3] = NX;
    dimsm[4] = NY;
    DataSpace memspace_map( RANK_OUT, dimsm );
    DataSpace memspace_rms( RANK_OUT, dimsm );
    DataSpace memspace_hit( RANK_OUT, dimsm );

    dataset_map.read( map, PredType::NATIVE_FLOAT, memspace_map, dataspace_map );
    dataset_rms.read( rms, PredType::NATIVE_FLOAT, memspace_map, dataspace_map );
    dataset_hit.read( hit, PredType::NATIVE_INT, memspace_map, dataspace_map );


    return 0;
}