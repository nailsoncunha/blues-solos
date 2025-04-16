#!/usr/bin/env python
#-*-coding: utf-8 -*-

import sys, pydot, subprocess, random, os
import cPickle as pickle

from mxml_handler import mount_bt

import preprocessor


def create_graph(dictio):
	"""
	Monta o grafo a partir de um dicionario recebido.
	Formato do dicionário: {
		origem: destino
	}. 
	Os objetos chave: valor são do tipo int.
	"""
	graph = pydot.Dot(graph_type='digraph')
	for key, value in dictio.iteritems():
		graph.add_edge(pydot.Edge(key, value))
		
	graph.write_png('graph_tour.png', prog='neato')
	#print "Grafo gerado."


def get_route(route_file, lick_list):
    """
    Lê o arquivo que contem a "rota" dos licks no formato origem,destino
    e retorna uma lista na ordem da sequencia dos licks.
    """
    f = open(route_file,'r+b')
    pairs = {}
    route = [0,]
#    final_route = []
    point = 0

    for line in f:
        pair = tuple(line.strip().split(","))
        pairs[int(pair[0])] = int(pair[1])		
	
    while 1:
        route.append(pairs.get(point))
        point = pairs.get(point)
        if point == 0:
            break
	
    f.close()
	
#	create_graph(pairs)
    route.pop()
    return route


def licks_draft(qtt, lfolder):
    total_licks = len( os.listdir( '%s/files/xml/%s' %(os.getcwd(), lfolder) ) )
    random.seed()
    licks = []

    while len(licks) < qtt:
        l = random.randint(1,total_licks)
        if l not in licks:
            licks.append(l)
            # print len(licks) , qtt
    return dict(enumerate(licks,1))



def save_pool(pool):
    with open('pool.p','wb+') as f:
        pickle.dump(pool, f, pickle.HIGHEST_PROTOCOL)


def load_pool():
    with open('pool.p','rb') as f:
        return pickle.load(f)


def createpool(argv):
    lspeed = argv[3] # s -> slow, m -> moderate, f -> fast
    qtt = int(argv[1]) # quantidades de licks do sorteio

    if lspeed in ['s', 'S']:
        lfolder = 'slow'
    elif lspeed in ['m', 'M']:
        lfolder = 'moderate'
    elif lspeed in ['f', 'F']:
        lfolder = 'fast'

    # lick_list = [x for x in range(total_licks+1)]
    lick_dict = licks_draft(qtt, lfolder)
    save_pool(lick_dict)


def make_randoms(lick_dict):
    random.seed()
    route = [0,]
    points = lick_dict.keys()
    for i in range(10):
        route.append(points[random.randint(0,len(points)-1)])
    ta = random.randint(1,13)
    route.append(points[-1]+1)
    lick_dict[points[-1]+ta] = ta

    print route
    print lick_dict
    return route



if __name__ == "__main__":
    """
    sys.argv[1] eh a quantidade de licks sorteados para o pool.
    sys.argv[2] eh a quantidade de compassos disponiveis para o solo. 13 eh porque conta com o dummy
    sys.argv[3] eh a lspeed do solo, licks e do BT
    sys.argv[4] eh a option de criacao dos solos aproveitando o mesmo pool. {0 nao modifica o funcionamento padrao,
        1 gera aleatorios, 2 gera os few rules, 3 gera os full rules, createpool para criar um novo pool de licks }
    """
    random.seed()
    if len(sys.argv) == 5:

        if sys.argv[4] == 'createpool':
            createpool(sys.argv)
            print 'Pool p/ Instancia %s criado' % sys.argv[1]
            sys.exit(0)

        lspeed = sys.argv[3] # s -> slow, m -> moderate, f -> fast
        qtt = int(sys.argv[1]) # quantidades de licks do sorteio
        pooloption = int(sys.argv[4])

        if lspeed in ['s', 'S']:
            lfolder = 'slow'
        elif lspeed in ['m', 'M']:
            lfolder = 'moderate'
        elif lspeed in ['f', 'F']:
            lfolder = 'fast'

        # lick_list = [x for x in range(total_licks+1)]
        if pooloption == 0:
            lick_dict = licks_draft(qtt, lfolder)
            total_licks, ta_diff = preprocessor.main_full(lfolder, lick_dict, qtt)
        elif pooloption == 1:
            lick_dict = load_pool()
            for i in range(30):
                route = make_randoms(lick_dict)
                mount_bt(route, lspeed, qtt, lick_dict, speed='moderate_blues')
            print 'randoms criados'
            sys.exit(0)
        elif pooloption == 2:
            lick_dict = load_pool()
            total_licks, ta_diff = preprocessor.main_few(lfolder, lick_dict, qtt)
        elif pooloption == 3:
            lick_dict = load_pool()
            total_licks, ta_diff = preprocessor.main_full(lfolder, lick_dict, qtt)

        # total_licks, ta_diff = preprocessor.main(lfolder, lick_dict, qtt) # Pega de retorno o tamanho total dos licks e o valor que será usado pra descobrir o índice do TA

        # proc = subprocess.Popen(['./bin/bySubtour',sys.argv[1],sys.argv[2]])
        proc = subprocess.Popen(['./bin/bySubtour',str(total_licks+1), sys.argv[2]])
        proc.wait()
        route_file = "route"
        route = get_route(route_file, lick_dict)
        print route
        # print lick_dict
        # mount_bt(route, lspeed, ta_diff, lick_dict, speed='moderate_blues')
        if pooloption == 2:
            mount_bt(route, lspeed, ta_diff, lick_dict, speed='moderate_blues', tune=False)
        else:
            mount_bt(route, lspeed, ta_diff, lick_dict, speed='moderate_blues', tune=False)

        
        for i in range(4):
            t = route[-1]
            p = route.pop(random.randint(0,len(route)-2))            
            prindex = open('prindex','ab+')
            prindex.write(str(p)+'\n') # Remove um lick aleatoriamente
            #prindex.write(str(t)+'\n') # Força a mudar o turnaround
            prindex.close()
            proc = subprocess.Popen(['./bin/bySubtour',str(total_licks+1), sys.argv[2]])
            proc.wait()
            route = get_route(route_file, lick_dict)
            print 'lick removido %d e %d\n' %(p, t)
            print route
            # print lick_dict
            if pooloption == 2:
                mount_bt(route, lspeed, ta_diff, lick_dict, speed='moderate_blues', tune=False)
            else:
                mount_bt(route, lspeed, ta_diff, lick_dict, speed='moderate_blues', tune=False)

        # prindex = open('prindex','w+b')
        # prindex.close()

    else:
        print "Faltando Parametros.\n Use: ./by_subtour.py <qtde. licks> <qtde. compassos> <speed>"
