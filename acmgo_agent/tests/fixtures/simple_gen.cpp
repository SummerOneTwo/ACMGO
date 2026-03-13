#include "testlib.h"
using namespace std;

int main(int argc, char* argv[]) {
    registerGen(argc, argv, 1);
    int seed = atoi(argv[1]);
    int type = atoi(argv[2]);
    int n_min = atoi(argv[3]);
    int n_max = atoi(argv[4]);
    int t_min = atoi(argv[5]);
    int t_max = atoi(argv[6]);

    rnd.seed(seed);
    int t = rnd(t_min, t_max);
    cout << t << "\n";
    forn(i, t) {
        int a = rnd(0, 1000);
        int b = rnd(0, 1000);
        cout << a << " " << b << "\n";
    }

    return 0;
}
