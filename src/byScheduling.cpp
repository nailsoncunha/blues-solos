
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <string.h>
#include <stdio.h>
#include <cstdlib>

#include <ilcplex/ilocplex.h>

#include "tools.h"

using namespace std;


int bysched(int instancia, int compassos){
    int i, j;
    
    //Environment
    IloEnv env;
    
    //Model
    IloModel modelo(env);        
    
    //Leitura da matriz de penalidades e da quant de compassos
    // de cada lick
    //double p[instancia][instancia];
    int c[instancia];
    
    double**p;    
    p = new double*[instancia];
    for(i = 0; i < instancia; i++)
    {
        p[i] = new double[instancia];
    }
    matriz_penalidades(p, instancia);
    compassos_licks(c, instancia);

    //Arrays das variáveis utilizadas no problema    
    IloArray <IloBoolVarArray> z(env,instancia);
    for(i=0;i<instancia;i++){
        IloBoolVarArray array(env,instancia);
        z[i] = array;
    }
    
    //Criando as variáveis Z
    char varName[100];
    for(i=0;i<instancia;i++){
        for(j=0;j<instancia;j++){
            if(i != j){
                sprintf(varName, "z_%d_%d", i, j);
                z[i][j].setName(varName);
                modelo.add(z[i][j]);
            }
        }
    }
    
    
    //Criação das Variáveis X usadas no problema
    IloArray <IloBoolVarArray> x(env,instancia);
    for(i=0;i<instancia;i++){
        IloBoolVarArray array(env,compassos);
        x[i] = array;
    }
    
    for(j=0;j<instancia;j++){
        for(int t=0; t < compassos-c[j]+1; t++){
            sprintf(varName, "x_%d_%d", j, t);
            x[j][t].setName(varName);
            modelo.add(x[j][t]);
        }
    }
    
    
    //Função Objetivo
    IloExpr fo(env);
    for(i=0; i<instancia; i++){
        for(j=0; j<instancia; j++){
            if(i != j)
                fo += p[i][j] * z[i][j];
        }
    }
    modelo.add(IloMinimize(env,fo));
    

    //Restrições de lick l usado no tempo t ( l in t )
    char cName[100];
    for(j=0;j<instancia;j++){
        IloExpr lint(env);
        for(int t=0; t < compassos-c[j]+1 ;t++){
            lint += x[j][t];
        }
        IloConstraint constr = (lint <= 1);
        sprintf(cName,"c1_%d",j);
        constr.setName(cName);
        modelo.add(constr);        
    }
    
    
    //Restrição de preenchimento dos slots dos compassos (j in s)
    int s;
    for(int t=0; t < compassos; t++){
        IloExpr jins(env);
        for(j=0;j<instancia;j++){
            s = max(0, t-c[j]+1);
            for(s ; s <= t ; s++){
                if(s+c[j] <= compassos){
                    jins += x[j][s];
                }
            }
        }        
        IloConstraint constr2 = (jins == 1);
        sprintf(cName,"c2_%d",t);
        constr2.setName(cName);
        modelo.add(constr2);
    }
    
    
    //Ultimo conjunto de restricoes z in j
    for(i=0;i<instancia;i++){
        for(j=0;j<instancia;j++){
            if( i!= j ){
                for(int t = 0; t < compassos-c[j]+1; t++){
                    if( t+c[i] < compassos-c[j]+1){
                        IloConstraint constr3 = (z[i][j] - x[i][t] - x[j][t+c[i]] >= -1);
                        sprintf(cName,"c3_%d_%d_%d",t,i,j);
                        constr3.setName(cName);
                        modelo.add(constr3);
                    }                
                }   
            }
        }
    }

    
    IloCplex cplex(env);
    //cplex.setOut(env.getNullStream());
    cplex.extract(modelo);
    cplex.exportModel("byScheduling.lp");
    
    cplex.solve();
     

    return 0;
}
