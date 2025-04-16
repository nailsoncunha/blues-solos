

#include <float.h>

#include <iostream>
#include <vector>
#include <list>
#include <string>

#include "MyCutCallbackMinCut.h"
#include "DataStructures.h"

using namespace std;

//código do callback que é executado pelo cplex.
int CPXPUBLIC mycutcallback (CPXCENVptr env, void *cbdata, int wherefrom, void *cbhandle, int *useraction_p)
{
    int status = 0;
    static pthread_mutex_t cs_mutex = PTHREAD_MUTEX_INITIALIZER;
    pthread_mutex_lock(&cs_mutex);

    int i, j, k, m, numCutsMB;
    char objName[100];

    int ndepth;
    int numCols;
    double *x;
    double **solX;
    double eps = 0.00000001;

    //Max-Back variables
    vector <double> b;
    vector <int> Sinit;
    vector <int> S;
    vector <int> Smin;
    double cutmin;
    double cutval;
    double max;
    int vertex;
    //-------------------

    //Min-Cut variables
    vector <vector<double> > arcs;
    vector <double> aux;
    vector <vector<int> > nodes;
    vector <int> nAux;
    vector <int> cutSet;
    vector <vector<int> > poolCutSet;

    int a;
    int flag;
    double l, cutphase, cut;
    //-------------------

    CPXLPptr model;
    PtrProblemData sptrPData;

    *useraction_p = CPX_CALLBACK_DEFAULT; 

    CPXgetcallbacknodeinfo (env, cbdata, wherefrom, 0, CPX_CALLBACK_INFO_NODE_DEPTH, &ndepth);

    //if (ndepth == 0) {
    sptrPData = (PtrProblemData) cbhandle;
    model = (*sptrPData).model;
    numCols = (*sptrPData).numCols;

    x = new double[numCols];
    CPXgetcallbacknodex (env, cbdata, wherefrom, x, 0, numCols-1);

    solX = new double*[(*sptrPData).numPoints];

    for (i = 0; i < (*sptrPData).numPoints; i++) {
       solX[i] = new double[(*sptrPData).numPoints];
       for (j = 0; j < (*sptrPData).numPoints; j++) {
	  solX[i][j] = 0;
       }
    }

    for (k = 0; k < numCols; k++)
    {    
       string s = getCollumName(env, model, k);
       if (s.at(0) == 'Z') 
       {
          strncpy(objName, s.c_str(), 100); 
          sscanf(objName, "Z(%d,%d)", &i, &j);
          solX[i][j] = solX[j][i] = x[k]; // index correction (laguage C begin at 0, TSP at 1)
          //printf("Z(%d,%d) = %f\n", i,j,solX[j][i]);

       }
    }

   std::vector<bool> isSingleton((*sptrPData).numPoints, true);
   //preenche isSingleton
   for(int ii = 0; ii < (*sptrPData).numPoints; ii++)
   {
      for(int jj = ii+1; jj < (*sptrPData).numPoints; jj++)
      {
	 if(solX[ii][jj] > 0)
	 {
	    isSingleton[ii] = isSingleton[jj] = false;
	 }
      }
   }

   //determinas os ids dos vertices nao singletons
   int nextVertexIdx = 0;
   int n_vertices = 0;
   std::vector<int> vertexIndex;
   for(i = 0; i < (*sptrPData).numPoints; i++)
   {
      if(not isSingleton[i])
      {
         vertexIndex.push_back(i);
         nextVertexIdx++;
         n_vertices++;
      }
   }


   // Max-Back algorithm ------------------------------------//
   list <int> LC;

   for(i = 0; i < n_vertices; i++)
   {
      LC.push_back(i);
   }

   for(i = 0; i < n_vertices; i++)
   {
      b.push_back(0.0);
   }

   numCutsMB = 0;
   do{
      vertex = LC.front();
      Sinit.push_back(vertex); //Adding vertex 0 to S0

      cutmin = 0.0;
      for(i = 0; i < n_vertices; i++)
      {
	    for(j = 0; j < Sinit.size(); j++){
	       //cutmin += solX[Sinit[j]][i];
	       cutmin += solX[vertexIndex[Sinit[j]]][vertexIndex[i]];
	    }
      }

      for(i = 0; i < n_vertices; i++)
      {
	 for(j = 0; j < Sinit.size(); j++)
	 {
	    if(i != Sinit[j])
	       // b[i] += solX[Sinit[j]][i];
	       b[i] = solX[vertexIndex[Sinit[j]]][vertexIndex[i]];
	 }
      }

      for(i = 0; i < Sinit.size(); i++)
      {
	 S.push_back(Sinit[i]);
	 Smin.push_back(Sinit[i]);
      }

      cutval = cutmin;


      while(S.size() < LC.size())
      {
	 max = -1.0;
	 int flag = 0;
	 for(i = 0; i < b.size(); i++){
	    for(j = 0; j < S.size(); j++){
	       if(i == S[j]){
		  flag = 1;
		  break;
	       }
	    }
	    if((flag == 0) && (b[i] > max)){
	       max = b[i];
	       vertex = i;
	    }
	    flag = 0;
	 }
	 S.push_back(vertex);
	 cutval += 2 - (2 * b[vertex]);

	 flag = 0;
	 for(i = 0; i < n_vertices; i++){
	    for(j = 0; j < S.size(); j++){
	       if(i == S[j]){
		  flag = 1;
		  break;
	       }
	    }
	    if((flag == 0)){
	       if(vertexIndex[vertex] < vertexIndex[i])
	       {
		  //  b[i] += solX[vertex][i];
		  b[i] += solX[vertexIndex[vertex]][vertexIndex[i]];
	       }
	       else
	       {
		  // b[i] += solX[i][vertex];
		  b[i] += solX[vertexIndex[i]][vertexIndex[vertex]];
	       }
	    }
	    flag = 0;
	 }

	 if(cutval < (cutmin - eps)){
	    cutmin = cutval;
	    Smin.clear();
	    for(j = 0; j < S.size(); j++){
	       Smin.push_back(S[j]);
	    }
	 }
      }

      if(Smin.size() < n_vertices)
      {
	 int cutnz = 0;
	 int colindex;
	 vector<int> cutindAux;
     //printf("size %d",Smin.size()); 
	 for(i = 0; i < Smin.size(); i++)
	 {
	    for(j = 0; j < Smin.size(); j++)
	    {
	       if(vertexIndex[Smin[i]] < vertexIndex[Smin[j]])
	       {
               
		  cutnz++;
		  sprintf(objName, "Z(%d,%d)", vertexIndex[Smin[i]], vertexIndex[Smin[j]]);
		  CPXgetcolindex (env, model, objName, &colindex);
		  cutindAux.push_back(colindex);
	       }
	    }
	    }

	 int *cutind = new int[cutnz];
	 double *cutcoef = new double[cutnz];
	 for(i = 0; i < cutnz; i++)
	 {
	    cutind[i] = cutindAux[i];
	    cutcoef[i] = 1;
	 }

	 double RHS = Smin.size() - 1;
	 status = CPXcutcallbackadd (env, cbdata, wherefrom, cutnz, RHS, 'L', cutind, cutcoef, 1);
	 if ( status ) {
	    fprintf (stderr, "Failed to add cut.\n");
	 }else{
	    //cout << "Max-Back Cut applied" << endl;
	    numCutsMB++;
	 }

	 delete[] cutind;
	 delete[] cutcoef;
      }

      Sinit.clear();
      S.clear();
      for(i = 0; i < n_vertices; i++)
      {
	 b[i] = 0.0;
      }

      for(i = 0; i < Smin.size(); i++){
	 LC.remove(Smin[i]);
      }
      Smin.clear();
      //cout << "Size LC: " << LC.size() << endl;
      //getchar();
   }while(LC.size() > 0);
   // Max-Back algorithm ------------------------------------//


   // Min-Cut algorithm ------------------------------------//
   //cout << "Depth: " << ndepth << endl;
   if(ndepth <= 7) 
   {
      if(numCutsMB == 0)
      {
	 nAux.push_back(0);
	 for(i = 0; i < n_vertices; i++){
	    aux.push_back(0.0);
	 }

	 for(i = 0; i < n_vertices; i++){
	    arcs.push_back(aux);
	    nAux[0] = i;
	    nodes.push_back(nAux);
	 }

	 for(i = 0; i < n_vertices; i++){
	    for(j = i+1; j < n_vertices; j++)
	    {
	    //   arcs[i][j] = solX[i][j];
	     //  arcs[j][i] = solX[i][j];
	       arcs[i][j] = arcs[j][i] = solX[vertexIndex[i]][vertexIndex[j]];
	    }
	 }

	 //MinCutPhase
	 a = 0;
	 cutphase = DBL_MAX;
	 while(nodes.size() > 1)
	 {
	    nAux.clear();
	    nAux.push_back(a);
	    while(nAux.size() < nodes.size()){
	       l = -1.0;
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
	       //cout << "k = " << k;
	       //getchar();
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

	    if(cut < cutphase){
	       cutphase = cut;
	       cutSet = nodes[k];
	    }
	    /*printf("CutS: ");
	      for(i = 0; i < nodes[k].size(); i++){
	      printf("%d ", nodes[k][i]);
	      }
	      printf("\n\n");*/


	    vector <int> cutAux;
	    if(nodes[k].size() <= (n_vertices / 2))
	       cutAux = nodes[k];
	    else{
	       for(i = 0; i < n_vertices; i++){
		  m = 0;
		  while((m < nodes[k].size()) && (nodes[k][m] != i)){ m++; }
		  if(m == nodes[k].size())
		  {
		     cutAux.push_back(i);
		  }
	       }
	    }

	    cutval = 0.0;
	    for(i = 0; i < (cutAux.size() - 1); i++)
	    {
	       for(m = i+1; m < cutAux.size(); m++)
	       {
		 /* if(cutAux[i] < cutAux[m])
		  {
		     cutval += solX[cutAux[i]][cutAux[m]];
		  }else
		  {
		     cutval += solX[cutAux[m]][cutAux[i]];
		  }
		  */
		  
		  cutval += solX[vertexIndex[cutAux[m]]][vertexIndex[cutAux[i]]];
	       }
	    }

	    if(cutval > (cutAux.size() - 1 + eps))
	    {
	       poolCutSet.push_back(cutAux);
	    }

	    for(i = 0; i < nodes[k].size(); i++)
	    {
	       nodes[j].push_back(nodes[k][i]);
	    }
	    nodes.erase(nodes.begin() + k);

	    /*printf("\n\nNodes:----------------\n");
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
	      printf("%.2lf ", arcs[i][j]);
	      }
	      printf("\n");
	      }
	      printf("------------\n\n");*/
	 }

	 //escreve os cortes
	 if(poolCutSet.size() > 0)
	 {
	    for(m = 0; m < poolCutSet.size(); m++)
	    {
	       cutSet = poolCutSet[m];
	       int cutnz = 0;
	       int colindex;
	       vector <int> cutindAux;

	       for(i = 0; i < cutSet.size(); i++){
		  for(j = 0; j < cutSet.size(); j++){
		     if(cutSet[i] < cutSet[j]){
			cutnz++;

			sprintf(objName, "Z(%d,%d)", vertexIndex[cutSet[i]], vertexIndex[cutSet[j]]);
			CPXgetcolindex (env, model, objName, &colindex);
			cutindAux.push_back(colindex);
		     }
		  }
	       }
	       int *cutind = new int[cutnz];
	       double *cutcoef = new double[cutnz];
	       for(i = 0; i < cutnz; i++){
		  cutind[i] = cutindAux[i];
		  cutcoef[i] = 1;
	       }

	       double RHS = cutSet.size() - 1;
	       status = CPXcutcallbackadd (env, cbdata, wherefrom, cutnz, RHS, 'L', cutind, cutcoef, 1);
	       if ( status ) {
		  fprintf (stderr, "Failed to add cut.\n");
	       }else{
		  //cout << "Min-Cut cut applied" << endl;
	       }

	       delete[] cutind;
	       delete[] cutcoef;
	    }
	 }
      }
   }
   // Min-Cut algorithm ------------------------------------//
   
    pthread_mutex_unlock(&cs_mutex);
    return(status);
}

string getCollumName(CPXCENVptr cpxEnv,  CPXLPptr  cpxModel, int collumIndex)
{
    int surplus;
    CPXgetcolname (cpxEnv, cpxModel, NULL, NULL, 0, &surplus, collumIndex, collumIndex);
    int storespace = - surplus;

    char* aux=new char[storespace];
    char** colname;
    colname = new char*[1];
    strcat(colname[0],"");

    int largestNameLength = 100;
    CPXgetcolname(cpxEnv,cpxModel,colname,aux,largestNameLength,&surplus,collumIndex,collumIndex);

    string result(colname[0]);

    delete[] colname;
    delete[] aux;
    return result;
}
