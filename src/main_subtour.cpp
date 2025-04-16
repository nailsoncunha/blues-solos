/************************************************************************************/
/*Project: TSP                                                                      */
/*Project description: Implementation of exact algorithms for TSP                   */
/*Filename: TSP.cpp                                                                 */
/*Description:                                                                      */
/*Author: Marcos Melo                                                               */
/*Date: 2011-06-09                                                                  */
/************************************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <float.h>

#include <vector>
#include <fstream>

#include <ilcplex/ilocplex.h>

#include "tools.h"
#include "DataStructures.h"
#include "MyCutCallbackMinCut.h"
#include "byRoutingFlow.h"

//#define SHOW_DEBUG
//#define SHOW_PROBLEMDATA
//#define SHOW_SOLUTIONDATA


using namespace std;

void Labeling(ProblemData *sptrPData, SolutionData *sptrSData);
void MinCut();

int main(int argc, char *argv[])
{
    if(argc < 3){
        cout << "Faltando parametros (Instancia, N. de Compassos).\n";
        return 0;
    }
    
    int total_licks, compassos;
    total_licks = atoi(argv[1]);
    compassos = atoi(argv[2]);
    
    //printf("Licks: %d, Compassos: %d.\n",total_licks, compassos);
    
    ProblemData *sptrPData = NULL;
    SolutionData *sptrSData = NULL;
    //AlgorithmData *sptrAData = NULL;

    int i, j, k;

    clock_t tRead_init, tRead_end;
    clock_t tAlg_init, tAlg_end;

    char objName[100];
    int status = 0;
    int numCols;
    double time, cplexTimeBefore, cplexTimeAfter;
    double *x;
    double cost;
    

    double**p;
    
    p = new double*[total_licks];
    for(i = 0; i < total_licks; i++)
    {
        p[i] = new double[total_licks];
    }
    
    matriz_penalidades(p,total_licks);

    sptrPData = new ProblemData;
    (*sptrPData).numPoints = total_licks;
    (*sptrPData).costMatrix = p;

    sptrSData = new SolutionData;

    #ifdef SHOW_PROBLEMDATA
        printf("\nNumber os points: %d\n", (*sptrPData).numPoints);
        printf("Points: ");
        //for(i = 0; i < (*sptrPData).numPoints; i++){
        //    printf("%d ", ((*sptrPData).points[i]));
        //}
        //printf("\n\n");

        printf("Costs Matrix: \n");
        for(i = 0; i < (*sptrPData).numPoints; i++){
            for(j = 0; j < (*sptrPData).numPoints; j++){
                printf("[%.2f]", (*sptrPData).costMatrix[i][j]);
            }
            printf("\n");
        }
        printf("\n\n");
    #endif

    tAlg_init = clock();
    //*************************************************************
//    CreateLP(sptrPData);
    byrflow(total_licks, compassos);

    // Initialize the cplex environment
    CPXENVptr env;
    CPXLPptr model;

    env = CPXopenCPLEX(&status);
    model = CPXcreateprob(env, &status, "LicksProblem");

    CPXreadcopyprob(env, model, "byRoutingFlow.lp", NULL);
    (*sptrPData).model = model;

    numCols = CPXgetnumcols(env, model);
    printf("\nNumber of columns: %d\n", numCols);
    (*sptrPData).numCols = numCols;

    // Parameters
    CPXsetintparam (env, CPX_PARAM_SCRIND, CPX_ON);
    CPXsetintparam (env, CPX_PARAM_MIPINTERVAL, 100);
    CPXsetintparam (env, CPX_PARAM_PRELINEAR, 0);
    CPXsetintparam (env, CPX_PARAM_MIPCBREDLP, CPX_OFF);
    CPXsetintparam (env, CPX_PARAM_THREADS, 1);

    CPXsetdblparam (env, CPX_PARAM_EPGAP, 1e-6);

    // Necessary when the formulation is incomplete
    CPXsetintparam (env, CPX_PARAM_REDUCE, CPX_PREREDUCE_PRIMALONLY);
    
    //CPXsetdblparam (env, CPX_PARAM_CUTUP, atof(argv[2]));
    CPXsetcutcallbackfunc (env, mycutcallback, sptrPData);

    CPXFILEptr fp;
    fp = CPXfopen("bySub.log", "w");

    // TODO Read MIPStart
    ///CPXreadcopymipstarts(env, model, objName);

    // Optimize
    CPXgettime(env, &cplexTimeBefore);

    CPXmipopt(env, model);

    CPXgettime(env, &cplexTimeAfter);
    time = cplexTimeAfter - cplexTimeBefore;


    x = new double[numCols];
    CPXgetx (env, model, x, 0, numCols-1);

    double **sol = new double*[(*sptrPData).numPoints];

    for (i = 0; i < (*sptrPData).numPoints; i++) {
        sol[i] = new double[(*sptrPData).numPoints];
        for (j = 0; j < (*sptrPData).numPoints; j++) {
            sol[i][j] = 0.0;
        }
    }
    
    ofstream route_file;
    route_file.open("route");

    cost = 0.0;
    cout << "\nSolution:" << endl;
    for (k = 0; k < numCols; k++) {    
        string s = getCollumName(env, model, k);
        if (s.at(0) == 'x') {
            strncpy(objName, s.c_str(), 100); 
            sscanf(objName, "x_%d_%d", &i, &j);
            sol[i][j] = x[k];       // index correction for C language
            if (sol[i][j] > 0.01) {
                cout << "x(" << i << "," << j << ") " << sol[i][j] << endl;
                route_file << i << "," << j << endl;
                cost += (*sptrPData).costMatrix[i][j];
            }
        }
    }
    
    route_file.close();
    printf("\nSolution cost: %lf\n\n", cost);

    delete[] x;

    for (i = 0; i < (*sptrPData).numPoints; i++) {
        delete[] sol[i];
    }
    delete[] sol;


    // Free memory
    CPXfclose(fp);
    CPXfreeprob(env, &model);
    CPXcloseCPLEX(&env);
    //*************************************************************/

    // Matrix memory allocation
    (*sptrSData).solutionMatrix = new double*[(*sptrPData).numPoints];
    for(i = 0; i < (*sptrPData).numPoints; i++){
        (*sptrSData).solutionMatrix[i] = new double[(*sptrPData).numPoints];
        for(j = 0; j < (*sptrPData).numPoints; j++){
            (*sptrSData).solutionMatrix[i][j] = 0.0;
        }
    }

    tAlg_end = clock();
    printf("\nAlgorithm run time: %lf\n", (tAlg_end - tAlg_init)/((double)CLOCKS_PER_SEC));

    // Free memory
    for(i = 0; i < (*sptrPData).numPoints; i++){
        delete [] (*sptrSData).solutionMatrix[i];
    }
    delete [] (*sptrSData).solutionMatrix;


    /*for(i = 0; i < (*sptrPData).numPoints; i++){
        //delete [] (*sptrPData).costMatrix[i];
    }
   // delete [] (*sptrPData).costMatrix;
    delete [] (*sptrPData).points;
    delete sptrPData;
*/
    return 0;
}


void MinCut()
{
    FILE *fp = NULL;
    
    vector <vector<double> > arcs;
    vector <double> aux;
    vector <vector<int> > nodes;
    vector <int> nAux;
    vector <int> cutSet;

    int a;
    int m, n;
    int i, j, k, flag;
    double l, cutphase, cut;

    fp = fopen("graph.txt", "r");
    if(fp == NULL){
        printf("\nFile open error\n");
    }else{
        fscanf(fp, "%d", &m);

        nAux.push_back(0);
        for(i = 0; i < m; i++){
            aux.push_back(0.0);
        }

        for(i = 0; i < m; i++){
            arcs.push_back(aux);
            nAux[0] = i;
            nodes.push_back(nAux);
        }

        fscanf(fp, "%d", &n);
        for(k = 0; k < n; k++){
            fscanf(fp, "%d %d %lf", &i, &j, &l);
            printf("\n(%d,%d):%lf", i, j, l);
            i--;
            j--;
            arcs[i][j] = l;
            arcs[j][i] = l;
        }
        printf("\n");
        fclose(fp);

        printf("\n\nNodes:----------------\n");
        for(i = 0; i < nodes.size(); i++){
            for(j = 0; j < nodes[i].size(); j++){
                printf("%d ", nodes[i][j]);
            }
            printf("\n");
        }
        printf("------------\n\n");
        printf("Arcs:----------------\n");
        for(i = 0; i < arcs.size(); i++){
            for(j = 0; j < arcs[i].size(); j++){
                printf("%lf ", arcs[i][j]);
            }
            printf("\n");
        }
        printf("------------\n\n");


        //MinCutPhase
        a = 0;
        cutphase = DBL_MAX;
        while(nodes.size() > 1){
            nAux.clear();
            nAux.push_back(a);
            while(nAux.size() < nodes.size()){
                l = 0.0;
                for(j = 0; j < nodes.size(); j++){
                    flag = 0;
                    for(i = 0; i < nAux.size(); i++){
                        if(nAux[i] == nodes[j][0]){
                            flag = 1;
                            break;
                        }
                    }

                    if(!flag){
                        for(i = 0; i < nAux.size(); i++){
                            if(arcs[nAux[i]][nodes[j][0]] > l){ 
                                l = arcs[nAux[i]][nodes[j][0]];
                                k = nodes[j][0];
                            }
                        }
                    }
                }
                nAux.push_back(k);
                cout << "k = " << k;
                getchar();
            }

            cut = 0.0;
            for(i = 0; i < nodes.size(); i++){
                if(arcs[nAux[nAux.size() - 1]][nodes[i][0]] > 0)
                    cut += arcs[nAux[nAux.size() - 1]][nodes[i][0]];

                if((arcs[nAux[nAux.size() - 2]][nodes[i][0]] > 0) && (arcs[nAux[nAux.size() - 1]][nodes[i][0]] > 0)){
                    arcs[nAux[nAux.size() - 2]][nodes[i][0]] += arcs[nAux[nAux.size() - 1]][nodes[i][0]];
                    arcs[nodes[i][0]][nAux[nAux.size() - 2]] += arcs[nAux[nAux.size() - 1]][nodes[i][0]];
                }else if((arcs[nAux[nAux.size() - 1]][nodes[i][0]] > 0) && (nAux[nAux.size() - 2] != nodes[i][0])){
                    arcs[nAux[nAux.size() - 2]][nodes[i][0]] += arcs[nAux[nAux.size() - 1]][nodes[i][0]];
                    arcs[nodes[i][0]][nAux[nAux.size() - 2]] += arcs[nAux[nAux.size() - 1]][nodes[i][0]];
                }
            }

            j = 0;
            while( (j < nodes.size()) && (nodes[j][0] != nAux[nAux.size() - 2]) ){
                j++;
            }
            
            k = 0;
            while( (k < nodes.size()) && (nodes[k][0] != nAux[nAux.size() - 1]) ){
                k++;
            }

            cout << "Cut: " << cut << endl;
            if(cut < cutphase){
                cutphase = cut;
                cutSet = nodes[k];
            }
            printf("CutS: ");
            for(i = 0; i < nodes[k].size(); i++){
                printf("%d ", nodes[k][i]);
            }
            printf("\n\n");

            for(i = 0; i < nodes[k].size(); i++){
                nodes[j].push_back(nodes[k][i]);
            }
            nodes.erase(nodes.begin() + k);

            printf("\n\nNodes:----------------\n");
            for(i = 0; i < nodes.size(); i++){
                for(j = 0; j < nodes[i].size(); j++){
                    printf("%d ", nodes[i][j]);
                }
                printf("\n");
            }
            printf("------------\n\n");
            printf("Arcs:----------------\n");
            for(i = 0; i < arcs.size(); i++){
                for(j = 0; j < arcs[i].size(); j++){
                    printf("%lf ", arcs[i][j]);
                }
                printf("\n");
            }
            printf("------------\n\n");
            getchar();
        }
        
        printf("min-cut: %lf\n", cutphase);
        printf("CutSet: ");
        for(i = 0; i < cutSet.size(); i++){
            printf("%d ", cutSet[i]);
        }
        printf("\n\n");
    }
}


void Labeling(ProblemData *sptrPData, SolutionData *sptrSData)
{
    int SIZE = 4;
    short int foundSink = 1;
    int source, sink;

    double delta;

    double **adjMatrix, **residMatrix;
    int *predecessor, *labels;
    vector<int> L;

    int i, j;
    int nodeAtual;

    //Matrix memory allocation
    adjMatrix = new double*[SIZE];
    residMatrix = new double*[SIZE];
    for(i = 0; i < SIZE; i++){
        adjMatrix[i] = new double[SIZE];
        residMatrix[i] = new double[SIZE];
        for(j = 0; j < SIZE; j++){
            adjMatrix[i][j] = 0.0;
            residMatrix[i][j] = 0.0;
        }
    }
    adjMatrix[0][1] = 2.0; residMatrix[0][1] = 5.0;
    adjMatrix[0][2] = 4.0; residMatrix[0][2] = 1.0;
    adjMatrix[1][2] = 3.0; residMatrix[1][2] = 3.0;
    adjMatrix[1][3] = 1.0; residMatrix[1][3] = 1.0;
    adjMatrix[2][3] = 5.0; residMatrix[2][3] = 7.0;
    
    printf("\nResidual Net:\n");
    for(i = 0; i < SIZE; i++){
        for(j = 0; j < SIZE; j++){
            printf("%.2lf ", residMatrix[i][j]);
        }
        printf("\n");
    }
    printf("\n");

    predecessor = new int[SIZE];
    labels = new int[SIZE];

    source = 0; sink = 3;
    do{
        for(i = 0; i < SIZE; i++){
            predecessor[i] = -1;
            labels[i] = 0;
        }

        L.push_back(source);
        labels[source] = 1;

        while(L.size() > 0){
            nodeAtual = L.front();
            L.erase(L.begin() + 0);

            for(j = 0; j < SIZE; j++){
                if( (labels[j] == 0) && (residMatrix[nodeAtual][j] > 0) ){
                    predecessor[j] = nodeAtual;
                    labels[j] = 1;
                    L.push_back(j);
                }
            }
            printf("Labels: ");
            for(i = 0; i < SIZE; i++){
                printf("%d ", labels[i]);
            }
            printf("\n");
            printf("L: ");
            for(i = 0; i < L.size(); i++){
                printf("%d ", L[i]);
            }
            printf("\n\n");
        }
        printf("Predecesors: ");
        for(i = 0; i < SIZE; i++){
            printf("%d ", predecessor[i]);
        }
        printf("\n");

        delta = DBL_MAX;
        if(labels[sink]){
            i = -1;
            j = sink;
            do{
                i = predecessor[j];
                if(residMatrix[i][j] < delta){
                    delta = residMatrix[i][j];
                }
                j = i;
            }while(i != source);
            printf("Delta: %lf\n", delta);

            i = -1;
            j = sink;
            do{
                i = predecessor[j];
                residMatrix[i][j] -= delta;
                j = i;
            }while(i != source);
        }else{
            foundSink = 0;
        }

        printf("\nResidual Net:\n");
        for(i = 0; i < SIZE; i++){
            for(j = 0; j < SIZE; j++){
                printf("%.2lf ", residMatrix[i][j]);
            }
            printf("\n");
        }
        printf("\n");
        //getchar();
        
    }while(foundSink);
    
    //Free memory
    for(i = 0; i < SIZE; i++){
        delete [] adjMatrix[i];
        delete [] residMatrix[i];
    }
    delete [] adjMatrix;
    delete [] residMatrix;

    delete [] predecessor;
    delete [] labels;
}



