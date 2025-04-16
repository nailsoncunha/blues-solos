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


int byrflow(int instancia, int compassos){
    
    int i, j;    
    IloEnv env;    
    IloModel modelo(env);        
    
    //Leitura da matriz de penalidades e da quant de compassos
    // de cada lick
   // double p[L][L];
    int c[instancia];
    int cindexes[instancia];
    int taindexes[instancia];
    int rindexes[instancia];
    int prindexes[instancia]; //Prohibited
    
    double**p;    
    p = new double*[instancia];
    for(i = 0; i < instancia; i++)
    {
        p[i] = new double[instancia];
    }
    matriz_penalidades(p, instancia);
    compassos_licks(c, instancia);
    coringa_index(cindexes);
    turnaround_index(taindexes);
    rest_index(rindexes);
    prohibited_index(prindexes);
    

    // for(i=0;i<instancia;i++){
    //     printf("%d\n",taindexes[i]);
    // }

    // return 0;



    //Array das Variáveis X 
    IloArray <IloBoolVarArray> x(env,instancia);
    for(i=0;i<instancia;i++){
        IloBoolVarArray array(env,instancia);
        x[i] = array;
    }
    
    //Adicionando as variaveis ao modelo
    char varName[100];
    for(i=0;i<instancia;i++){
        for(j=0;j<instancia;j++){
            if(i != j){
                sprintf(varName, "x_%d_%d", i, j);
                x[i][j].setName(varName);
                modelo.add(x[i][j]);
            }
        }
    }    
        
    //Função Objetivo
    IloExpr fo(env);
    for(i=0; i<instancia; i++){
        for(j=0; j<instancia; j++){
            if(i != j)
                fo += p[i][j] * x[i][j];
        }
    }
    modelo.add(IloMinimize(env,fo));
    
    
    //Criação das variáveis Y
    IloBoolVarArray y(env,instancia);
    
    //Adicionando Y ao modelo
    for(i=0;i<instancia;i++){
        sprintf(varName, "y_%d", i);
        y[i].setName(varName);
        modelo.add(y[i]);
    }
    
    //Restrições de lick l usado y "avisa"
    char cName[100];
    char cName2[100];
    for(i=0;i<instancia;i++){
        IloExpr l_used(env);
        IloExpr l_used2(env);
        for(j=0; j<instancia; j++){
            if(i != j){
                l_used += x[i][j];
                l_used2 += x[j][i];
            }
        }
        l_used -= y[i];
        l_used2 -= y[i];
        IloConstraint constr = (l_used == 0);
        IloConstraint constr2 = (l_used2 == 0);
        sprintf(cName,"c1_%d",i);
        sprintf(cName2,"c2_%d",i);
        constr.setName(cName);
        constr2.setName(cName2);
        modelo.add(constr);
        modelo.add(constr2);
    }
    
/*    
    //Restrições de fluxo
    //Array das Variáveis f 
    IloArray <IloBoolVarArray> f(env,L);
    for(i=0;i<L;i++){
        IloBoolVarArray array(env,L);
        f[i] = array;
    }
    
    //Adicionando as variaveis ao modelo
    for(i=0;i<L;i++){
        for(j=0;j<L;j++){
            if(i != j){
                sprintf(varName, "f_%d_%d", i, j);
                f[i][j].setName(varName);
                modelo.add(f[i][j]);
            }
        }
    } 
    
    //Criando as restrições
    for(int k=0;k<L;k++){
        IloExpr flow(env);
        IloExpr flow2(env);
        for(i=0;i<L;i++){
            if(i != k){
                flow += f[i][k];
            }            
        }
        for(j=0;j<L;j++){
            if(j != k){
                flow2 += f[k][j];
            }            
        }
        IloConstraint constr = (flow - flow2 -y[k] == 0);
        sprintf(cName,"c3_%d",k);
        constr.setName(cName);
        modelo.add(constr);
    }
    
    //Restrição de "Matar" o arco caso não seja usado
    for(i=0;i<L;i++){
        for(j=0;j<L;j++){
            if(i != j){
                IloConstraint constr = (f[i][j] - NC * x[i][j] <=0);
                sprintf(cName,"c4_%d_%d",i,j);
                constr.setName(cName);
                modelo.add(constr);
            }
        }
    }
*/  

    // Restrições de lick coringa
    // Usar opcionalmente e apenas um
    IloExpr coringas(env);
    for(i=0;i<instancia;i++){
        if (cindexes[i] == -1)
            break;
        coringas += y[cindexes[i]];
    }
    IloConstraint cor_constr = (coringas <= 1);
    cor_constr.setName("crg1");
    modelo.add(cor_constr);

    
    // Restrição de turnarounds
    // Forcar turnarounds no fim
    IloExpr turnarounds(env);
    for(i=0;i<instancia;i++){
        if (taindexes[i] == -1)
            break;
        // printf("ENTREI %d - %d\n", i, taindexes[i] );
        turnarounds += x[taindexes[i]][0];
        // printf("SAÍ\n");
    }
    IloConstraint ta_constr = (turnarounds == 1);
    ta_constr.setName("ta1");
    modelo.add(ta_constr);


    // Restrição de licks com pausa
    // Usar x licks ou menos, com pausa
    IloExpr rests(env);
    for(i=0;i<instancia;i++){
        if (rindexes[i] == -1)
            break;
        // printf("ENTREI %d - %d\n", i, rindexes[i] );
        rests += y[rindexes[i]];
        // printf("SAÍ\n");
    }
    IloConstraint rest_constr = (rests <= 3);
    rest_constr.setName("rest1");
    modelo.add(rest_constr);


    // Restrição de licks removidos
    // Licks proibidos de serem usados
    IloExpr prohib(env);
    for(i=0;i<instancia;i++){
        if (prindexes[i] == -1)
            break;
        // printf("ENTREI %d - %d\n", i, prindexes[i] );
        prohib += y[prindexes[i]];
        // printf("SAÍ\n");
    }
    IloConstraint prohib_constr = (prohib == 0);
    prohib_constr.setName("prohib1");
    modelo.add(prohib_constr);

    
    // Restrição de turnarounds
    // // Impedir turnarounds em outra posição para o 0, além do fim
    // IloExpr turnarounds2(env);
    // for(i=0;i<instancia;i++){
    //     if (taindexes[i] == -1)
    //         break;
    //     turnarounds2 += x[0][taindexes[i]];
    // }
    // IloConstraint ta_constr2 = (turnarounds2 == 0);
    // ta_constr2.setName("ta2");
    // modelo.add(ta_constr2);


    //Restrição de Numero de compassos
    IloExpr slots(env);
    for(i=0;i<instancia;i++)
    {
        slots += c[i] * y[i];
    }
    IloConstraint constr = (slots == compassos);
    constr.setName("c6");
    modelo.add(constr);
    
    
    IloArray <IloBoolVarArray> z(env,instancia);
    for(i=0;i<instancia;i++){
        IloBoolVarArray array(env,instancia);
        z[i] = array;
    }
    
    for(i=0;i<instancia;i++){
        for(j=0;j<instancia;j++){
            if(i < j){
                sprintf(varName, "Z(%d,%d)", i, j);
                z[i][j].setName(varName);
                modelo.add(z[i][j]);
            }
        }
    }
    
    
     for(i=0;i<instancia;i++){
        for(j=0;j<instancia;j++){
            if(i < j){
                IloConstraint constr = (x[i][j] + x[j][i] - z[i][j] == 0);
                sprintf(cName,"c7_%d_%d",i,j);
                constr.setName(cName);
                modelo.add(constr);
            }
        }
    }
    
    IloCplex cplex(env);
    //cplex.setOut(env.getNullStream());
    cplex.extract(modelo);
    cplex.exportModel("byRoutingFlow.lp");
    
    //cplex.solve();
}
