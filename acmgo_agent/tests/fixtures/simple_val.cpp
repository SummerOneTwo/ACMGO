#include "testlib.h"
using namespace std;

int main() {
    registerValidation();
    int t = inf.readInt(1, 10);
    inf.readEoln();
    forn(i, t) {
        inf.readInt(0, 1000);
        inf.readSpace();
        inf.readInt(0, 1000);
        inf.readEoln();
    }
    inf.readEof();
    return 0;
}
