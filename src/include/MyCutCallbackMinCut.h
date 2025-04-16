/************************************************************************************/
/*Project: TSP                                                                      */
/*Project description: Implementation of exact algorithms for TSP                   */
/*Filename: BCUtils.h                                                               */
/*Description:                                                                      */
/*Author: Marcos Melo                                                               */
/*Date: 2011-06-09                                                                  */
/************************************************************************************/

#ifndef BCUTILS_H
#define BCUTILS_H

#include <ilcplex/ilocplex.h>

//#include <TSPUtil.h>
#include <string>

int CPXPUBLIC mycutcallback (CPXCENVptr env, void *cbdata, int wherefrom, void *cbhandle, int *useraction_p);

std::string getCollumName(CPXCENVptr cpxEnv,  CPXLPptr  cpxModel, int collumIndex);

//void CreateLP(ProblemData *sptrPData);

#endif
