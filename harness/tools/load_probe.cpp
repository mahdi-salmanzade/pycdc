// Load-stage probe for the differential test harness (not part of pycdc).
//
// Runs only PycModule::loadFromFile() from the unmodified pycxx library, so a
// failure here is attributable to .pyc header / marshal / code-object loading
// rather than to disassembly or decompilation.  pycdas cannot be used for this
// because it does not check isValid() after loading and its buffered stdout
// is lost when it crashes.
//
// Build (done automatically by harness/difftest.py):
//   c++ -std=c++11 -I<repo> harness/tools/load_probe.cpp <build>/libpycxx.a

#include <cstdio>
#include <exception>
#include "pyc_module.h"

int main(int argc, char* argv[])
{
    if (argc != 2) {
        fputs("usage: load_probe input.pyc\n", stderr);
        return 2;
    }

    PycModule mod;
    try {
        mod.loadFromFile(argv[1]);
    } catch (std::exception& ex) {
        fprintf(stderr, "load exception: %s\n", ex.what());
        return 1;
    }
    if (!mod.isValid()) {
        fputs("load: module version not recognized\n", stderr);
        return 1;
    }
    if (mod.code() == nullptr) {
        fputs("load: no code object\n", stderr);
        return 1;
    }
    printf("ok %d.%d\n", mod.majorVer(), mod.minorVer());
    return 0;
}
