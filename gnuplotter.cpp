#include <string>
#include <chrono>
#include <armadillo>

#include "gnuplot-iostream.h"

using namespace std;


inline void gnuplotter(const int x, const int y, const arma::mat &image, string filename){
    Gnuplot gp;
    gp << "set term png\n";
    gp << "set output '" + filename + "' \n";
    gp << "set xrange[0:99]\n set yrange[0:99]\n";
    gp << "plot '-' binary" << gp.binFmt2d(image, "array") << "with image\n";
    gp.sendBinary2d(image);
}


int main(){
    const int x = 100;
    const int y = 100;
    arma::mat image(x, y, arma::fill::zeros);

    for(int i=0; i<x; i++){
        for(int j=0; j<y; j++){
            double x = (i-50.0)/5.0;
            double y = (j-50.0)/5.0;
            double z = std::cos(sqrt(x*x+y*y));
            image(i,j) = z;
        }
    }
    string filename = "test.png";
    gnuplotter(x, y, image, filename);

    return 0;
}