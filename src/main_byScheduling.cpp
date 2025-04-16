#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <string.h>
#include <stdio.h>
#include <cstdlib>

#include <ilcplex/ilocplex.h>

#include "tools.h"
#include "byScheduling.h"

using namespace std;

int main(int argc, char **argv)
{
    if(argc < 3){
        cout << "Faltando parametros (Instancia, N. de Compassos).\n";
        return 0;
    }
    
    int total_licks, compassos;
    total_licks = atoi(argv[1]);
    compassos = atoi(argv[2]);
    
	bysched(total_licks, compassos);
	return 0;
}
