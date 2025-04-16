#!/usr/bin/env python
#-*- coding: utf-8 -*-

from notes_handler import *

from time import gmtime, strftime
from lxml import etree

import sys, os, postprocessor

DROPBOX_PATH = "/home/nailson/Dropbox/My Documents/Projeto-Mestrado/Pesquisa operacional/licks-temp/Outputs"


def clean_measure(measure):
    """
    Recebe um ElementTree que representa a tag <measure> do 
    MusicXML. São removidos as tags attributes, sound e barline (caso
    exista mais de uma) para que não fiquem duplicadas no arquivo.
    Retorna o measure modificado.
    """
    if measure.find('attributes') is not None:
        measure.remove(measure.find('attributes'))
        
    if measure.find('sound') is not None:
        measure.remove(measure.find('sound'))
    
    if len(list(measure.iter('barline'))) > 1:
        measure.remove(measure.find('barline'))
    
    return measure



def measure_append(main_part, part):
    """
    Recebe dois ElementTree referentes a tag <part>.
    O primeiro é a <part> principal, onde serao adicionados
    os <measures> da outra part recebida como parametro.
    Retorna a main_part modificada.
    """
    #Pega o numero do ultimo compasso
    measures = list(main_part.iter('measure'))
    last_measure_number = int(measures[-1].get('number'))
    
    #Adiciona os demais compassos incrementando seus numeros
    for meas in part.iter('measure'):
        meas.set('number',str(last_measure_number+1))
        last_measure_number += 1
        meas = clean_measure(meas)
        main_part.append(meas)
        
    return main_part


def prepare_bt_tree(bt_tree, main_tree):
    main_root = main_tree.getroot()
    main_score = main_root.find('part-list').find('score-part')
    main_score.find('part-name').text = 'Solo'
    main_score.set('id','P4')
    main_score.find('score-instrument').set('id','P4-I4')
    main_score.find('midi-instrument').set('id','P4-I4')
    main_score.find('midi-instrument').find('midi-channel').text = '12'
    
    main_part = main_root.find('part')
    main_part.set('id',"P4")
    bt_root = bt_tree.getroot()
    bt_root.find('part-list').append(main_score)
    bt_root.append(main_part)
    return bt_tree

        

def mount_bt(order, lspeed, ta_diff, lick_dict, speed="medium_blues", tune=False):
    """
    Funcao que prepara o aquivo xml final que contera o backing track
    somado o solo gerado pelo otimizador.
    Recebe uma lista com a ordem dos licks e tambem uma string que 
    define a escolha do blues de acordo com a velocidade. slow_blues,
    medium_blues ou fast_blues.
    """
    # print 'Lspeed', lspeed
    if lspeed in ['s' ,'S']:
        lfolder = 'slow'
    elif lspeed in ['m', 'M']:
        lfolder = 'moderate'
    elif lspeed in ['f', 'F']:
        lfolder = 'fast'

    order.pop(0) # Removendo o Dummy da lista

    f_bt = open('files/xml/utils/%s.xml' %speed,'r+b')
    # print order[0]
    main_licks = open('files/xml/%s/%d.xml' %(lfolder, lick_dict.get(order[0])),'r+b')
    main_tree = etree.parse(main_licks)
    #main_tree = transpose('c', 'd', main_tree)
    main_root = main_tree.getroot()
    main_part = main_root.find('part')
    measures = list(main_part.iter('measure'))
    
    #Para que os compassos comecem do segundo.
    start = 1
    for meas in main_part.iter('measure'):
        if meas.find('sound') is not None:
            meas.remove(meas.find('sound')) #CORRIGIR ISSO E TENTAR REMOVER APENAS O ATRIBUTO TEMPO
            #meas.find('sound').pop('tempo')
        meas.set('number',str(start+1))
    
    turnaround = order.pop() # Retiro o ultimo elemento da lista, que é o TA
    for o in order[1:]:
        # print o
        f = open('files/xml/%s/%d.xml' %(lfolder, lick_dict.get(o)))
        tree = etree.parse(f)
        #tree = transpose('c', 'd', tree)
        root = tree.getroot()
        part = root.find('part')
        main_part = measure_append(main_part, part)
        f.close()
    
    # Acrescento o TA ao BT
    f = open('files/xml/turnaround/%d.xml' %(turnaround-ta_diff))
    tree = etree.parse(f)
    #tree = transpose('c', 'd', tree)
    root = tree.getroot()
    part = root.find('part')
    main_part = measure_append(main_part, part)
    f.close()

    bt_tree = etree.parse(f_bt)
    bt_root = bt_tree.getroot()


    if tune:
        main_tree = postprocessor.autotune(main_tree)
        
    bt_tree = prepare_bt_tree(bt_tree, main_tree)
    
    timenow = strftime("%Y%m%d%H%M%S", gmtime())
    out_file = open('%s/out-%s.xml' %(DROPBOX_PATH,timenow),'w+b')
    out_file.write(etree.tostring(bt_tree))
    
    order.append(turnaround) # Devolvo o turnaround pro order pra poder identifica-lo no by_subtour.py
    out_file.close()
    main_licks.close()
    f_bt.close()    



def get_lick_trees(lfolder, lick_dict):
    licks_trees_dict = {}    
    for i in lick_dict.keys():
        with open('%s/files/xml/%s/%d.xml' %(os.getcwd(), lfolder, lick_dict[i])) as t:
            licks_trees_dict[i] = etree.parse(t)

    return licks_trees_dict

def get_turns_trees(licks_trees):
    last_key = licks_trees.keys()[-1]
    turns = len( os.listdir( '%s/files/xml/turnaround' %os.getcwd() ) )
    for i in range(1,turns + 1):
        with open('%s/files/xml/turnaround/%d.xml' %(os.getcwd(), i ) ) as t:
            licks_trees[last_key+1] = etree.parse(t)
            last_key += 1

    return licks_trees



#Main utilizado apenas para teste
if __name__ == "__main__":
    sequence = ['01','02','03','04','07','08']
    
    first_file = open('/home/nailson/shared/licks/database/%s.xml' % sequence[0])
    main_tree = etree.parse(first_file)
    main_root = main_tree.getroot()
    main_part = main_root.find('part')
    first_file.close()
    
    for filename in sequence[1:]:
        f = open('/home/nailson/shared/licks/database/%s.xml' % filename)
        tree = etree.parse(f)
        root = tree.getroot()
        part = root.find('part')
        main_part = measure_append(main_part,part)
        f.close()
        
    out_file = open('/home/nailson/out-test.xml','w+b')
    out_file.write(etree.tostring(main_tree))
    out_file.close()
    print "Programa Finalizado."
