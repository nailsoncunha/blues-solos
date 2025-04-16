/************************************************************************************/
/*Project: TSP                                                                      */
/*Project description: Implementation of exact algorithms for TSP                   */
/*Filename: DataStructures.h                                                        */
/*Description:                                                                      */
/*Author: Marcos Melo                                                               */
/*Date: 2011-06-09                                                                  */
/************************************************************************************/

#ifndef DATASTRUCTURES_H
#define DATASTRUCTURES_H

//#include <list>
#include <ilcplex/ilocplex.h>

/*typedef struct TArc{
    int head;
    double lenght;
}Arc;

typedef struct TNode{
    std::list <int> tail;
    std::list <struct TArc> arcs;
}Node;*/

typedef struct TProblemData{
    CPXLPptr model;
    int numCols;

    unsigned int numPoints;
    unsigned int *points;
    double **costMatrix;
}ProblemData, *PtrProblemData;


typedef struct TSolutionData{
    double **solutionMatrix;
}SolutionData;


typedef struct TAlgorithmData{
}AlgorithmData;

#endif

