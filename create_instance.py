#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
import random


def create_random_instance(tamanho_inst):    
    if tamanho_inst > 1:
        f = open("files/instances/%d" %tamanho_inst,"w+b")
        f_compassos = open("files/instances/c_%d" %tamanho_inst, "w+b")
        matriz = []
        for i in range(tamanho_inst):
            matriz.append([random.randint(2,10) for x in range(tamanho_inst)])
        
        #Zerando as diagonais e "Lick Dummy"
        for i in range(tamanho_inst):
                for j in range(tamanho_inst):
                    if i==0 or j==0 or i == j:
                        matriz[i][j] = 0
                        
        #Tornando matriz[j][i] == matriz[i][j]
        for i in range(tamanho_inst):
            for j in range(i,tamanho_inst):
                matriz[j][i] = matriz[i][j]
                        
        #Escrevendo a Matriz no arquivo
        for i in range(tamanho_inst):
                for j in range(tamanho_inst):
                    f.write("%d\t" %matriz[i][j])
                f.write("\n")
                
        #Gerando numero de compassos dos licks
        for i in range(tamanho_inst):
            #if i == 0:
            #    f_compassos.write("0\n" )
            #else:
            f_compassos.write("1\n" )
            #%random.randint(1,2)
            
        
        print "Instância tamanho %d gerada." %tamanho_inst
    else:
        print "Tamanho da intância??"



def main(inst_size, matrix, total_licks, total_turns):
    
    if inst_size:
        f = open("files/instances/%d" %inst_size,"w+b")
        f_compassos = open("files/instances/c_%d" %inst_size, "w+b")
                        
        #Escrevendo a Matriz no arquivo
        for i in range(inst_size):
                for j in range(inst_size):
                    f.write("%d\t" %matrix[i][j])
                f.write("\n")
                
        #Gerando numero de compassos dos licks
        for i in range(inst_size+1):
            if i <= total_licks:
               f_compassos.write("1\n" )
            else:
                f_compassos.write("2\n" )
            
        
        print "Instância tamanho %d gerada." %inst_size
    else:
        print "Tamanho da intância??"


if __name__ == '__main__':
    main()