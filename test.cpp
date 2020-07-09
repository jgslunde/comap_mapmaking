#include <iostream>
#include <string>
#include <H5Cpp.h>
#include <H5File.h>

using namespace std;
using namespace H5;


const H5std_string FILE_NAME( "co6_good_hp_map.h5" );  // Name of h5 file.
const H5std_string DATASET_NAME( "map" );  // Name of dataset field.

const int    NX_SUB = 8;    // "hyperslab dimensions". Dimensions of 
const int    NY_SUB = 8;

const int    NFEED = 1;
const int    NBAND = 1;
const int    NFREQ = 1;
const int    NY = 8;
const int    NX = 8;        // output buffer dimensions

const int RANK_OUT = 5;  // Nr dims in matrix you're writing to. Seems like it must correspond to the dimensions in the h5.

int main(){
   float data_out[NFEED][NBAND][NFREQ][NX][NY]; /* output buffer */
    // We should technically do this for the entire array...:
    //    for (int i = 0; i < NX; i++){
    //        for (int j = 0; i < NY; i++)
    //         {
    //             data_out[i][j] = 0;
    //         }
    //     }
    
    H5File file( FILE_NAME, H5F_ACC_RDONLY );  // Open file.
    DataSet dataset = file.openDataSet( DATASET_NAME );  // Open dataset.

    H5T_class_t type_class = dataset.getTypeClass();  // Check type of dataset.

    if( type_class == H5T_FLOAT ){
        cout << "Data set has FlOAT type" << endl;
    }
    if( type_class == H5T_INTEGER ){
        cout << "Data set has INTEGER type" << endl;
    }
    /*
    * Get dataspace of the dataset.
    */
    DataSpace dataspace = dataset.getSpace();
    /*
    * Get the number of dimensions in the dataspace.
    */
    int rank = dataspace.getSimpleExtentNdims();

    hsize_t dims_out[2];
    int ndims = dataspace.getSimpleExtentDims( dims_out, NULL);
    cout << "rank " << rank << ", dimensions " <<
        (unsigned long)(dims_out[0]) << " x " <<
        (unsigned long)(dims_out[1]) << " x " <<
        (unsigned long)(dims_out[2]) << " x " <<
        (unsigned long)(dims_out[3]) << " x " <<
        (unsigned long)(dims_out[4]) << endl;

    /*
    * Define hyperslab in the dataset; implicitly giving strike and
    * block NULL.
    */
    // We define two arrays, one for the offset in each dimension, and one for the nr of items we want to read in that dimension.
    hsize_t      offset[5];   // hyperslab offset in the file
    hsize_t      count[5];    // size of the hyperslab in the file
    offset[0] = 0;  // 0,1,8,37,33
    offset[1] = 1;
    offset[2] = 8;
    offset[3] = 35;
    offset[4] = 35;
    count[0]  = 1;
    count[1]  = 1;
    count[2]  = 1;
    count[3]  = NX_SUB;
    count[4]  = NX_SUB;

    dataspace.selectHyperslab( H5S_SELECT_SET, count, offset );

    // Define the memory dataspace.
    hsize_t     dimsm[5];              /* memory space dimensions */
    dimsm[0] = 1;
    dimsm[1] = 1;
    dimsm[2] = 1;
    dimsm[3] = NX;
    dimsm[4] = NY;
    DataSpace memspace( RANK_OUT, dimsm );

    /*
    * Read data from hyperslab in the file into the hyperslab in
    * memory and display the data.
    */
    dataset.read( data_out, PredType::NATIVE_FLOAT, memspace, dataspace );
    for (int i = 0; i < NX; i++){
        for (int j = 0; j < NY; j++){
            cout << data_out[0][0][0][i][j] << " ";
        }
        cout << endl;
    }

    cout << "hello" << endl;

    return 0;
}