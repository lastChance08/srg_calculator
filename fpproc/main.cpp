#include <cstdlib>
#include <stdio.h>
#include <string.h>
#include "fpproc.h"
#include "femmcomplex.h"

using namespace std;

int main(int argc, char** argv)
{
    FPProc testFPProc;
    CComplex out;

    char PathName[512];

    if (argc < 2)
    {
        // request the file name from the user
        printf("Enter ans file name:\n");

        //char tempFilePath[512];

        //scanf("%s", tempFilePath);

        fgets(PathName, 512, stdin);
        char *pos;
        if ((pos=strchr(PathName, '\n')) != NULL)
            *pos = '\0';

        //PathName = tempFilePath;

    }
    else if(argc > 2)
    {
        printf("Too many arguments");
    }
    else
    {
        strcpy(PathName, argv[1]);
    }


    int loadAns = testFPProc.OpenDocument(PathName);

    if (loadAns==true)
    {
        out = testFPProc.GetFluxLinkage(0);
        std::cout << out.Re()/testFPProc.circproplist[0].Amps.Re();
    }

    return 0;
}
