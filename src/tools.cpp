#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <string.h>
#include <stdio.h>
#include <cstdlib>

#include <ilcplex/ilocplex.h>

#include "tools.h"

#define L 25
#define NC 24

using namespace std;

/*
 * NÃO ENTENDI BEM, COPIEI DA NET
 * Mas, contudo, funciona como uma função de split string.
 */
std::vector<std::string> split(std::string str,std::string sep){
    char* cstr=const_cast<char*>(str.c_str());
    char* current;
    std::vector<std::string> arr;
    current=strtok(cstr,sep.c_str());
    while(current!=NULL){
        arr.push_back(current);
        current=strtok(NULL,sep.c_str());
    }
    return arr;
}


/*
 * Recebe um array de inteiros que é a matriz de penalidades
 * e preenche a matriz.
 */
int matriz_penalidades(double** matriz, int instancia){
    string linha;
    char nome_arq[100];
    vector<string> arr;
    int row = 0;
    
    sprintf(nome_arq,"files/instances/%d",instancia);
    printf("%s\n", nome_arq);
    ifstream myfile(nome_arq);
    
    if ( myfile.is_open() ){
        while ( getline(myfile, linha) ) {
            arr = split(linha, "\t");
            for(int i=0;i<arr.size();i++)
                matriz[row][i] = atoi(arr[i].c_str());
            row++;
       }
       
       myfile.close();
    } else cout << "Nao abriu o arquivo!";
    
    return 0;
}


/*
 * Recebe um array de inteiros e lê de um arquivo a qntd de
 * compassos de cada lick. Preenche o array com o compassos dos licks.
 */
int compassos_licks(int compassos[], int instancia){
    string linha;
    char nome_arq[100];
    int i = 0;
    
    sprintf(nome_arq,"files/instances/c_%d",instancia);
    ifstream myfile(nome_arq);
    if ( myfile.is_open() ){
        while ( getline(myfile, linha) ) {
            compassos[i] = atoi(linha.c_str());
            i++;
       }
       
       myfile.close();
    } else cout << "Nao abriu o arquivo!";
    
    return 0;
}


int coringa_index(int cindexes[]){
    string linha;
    char nome_arq[100];
    int i = 0;
    
    sprintf(nome_arq,"cindex");
    ifstream myfile(nome_arq);
    if ( myfile.is_open() ){
        while ( getline(myfile, linha) ) {
            cindexes[i] = atoi(linha.c_str());
            i++;
       } 
       cindexes[i] = -1;
       
       myfile.close();
    } else cout << "Nao abriu o arquivo cindex!";
    
    return 0;

};


int turnaround_index(int taindexes[]){
    string linha;
    char nome_arq[100];
    int i = 0;
    
    sprintf(nome_arq,"taindex");
    ifstream myfile(nome_arq);
    if ( myfile.is_open() ){
        while ( getline(myfile, linha) ) {
            taindexes[i] = atoi(linha.c_str());
            i++;
       }
       taindexes[i] = -1;
       
       myfile.close();
    } else cout << "Nao abriu o arquivo taindex!";
    
    return 0;

};


int rest_index(int rindexes[]){
    string linha;
    char nome_arq[100];
    int i = 0;
    
    sprintf(nome_arq,"rindex");
    ifstream myfile(nome_arq);
    if ( myfile.is_open() ){
        while ( getline(myfile, linha) ) {
            rindexes[i] = atoi(linha.c_str());
            i++;
       }
       rindexes[i] = -1;
       
       myfile.close();
    } else cout << "Nao abriu o arquivo rindex!";
    
    return 0;
};


int prohibited_index(int prindexes[]){
    string linha;
    char nome_arq[100];
    int i = 0;
    
    sprintf(nome_arq,"prindex");
    ifstream myfile(nome_arq);
    if ( myfile.is_open() ){
        while ( getline(myfile, linha) ) {
            prindexes[i] = atoi(linha.c_str());
            //cout << "passando pelo prindex! " << "\n";
            i++;
       }
       prindexes[i] = -1;
       
       myfile.close();
    } else cout << "Nao abriu o arquivo prindex!";
    
    return 0;
};