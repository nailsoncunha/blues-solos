#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

from lxml import etree

note_dict = {'REST': 0, 'C': 1, 'C#': 2, 'D': 3, 'D#':4, 'E': 5,
            'F': 6, 'F#': 7, 'G': 8, 'G#': 9, 'A': 10, 'A#': 11, 'B': 12}
            
tech_dict = {'bend': 0, 'slide': 1, 'hammer': 2, 'pull': 3, 'b-release': 4} 

duration_index = {'whole': 0, 'half': 1, 'quarter':2, 'eighth': 3, '16th': 4, '32th': 5}
duration_values = {'whole': 1, 'half': 2, 'quarter':4, 'eighth': 8, '16th': 16, '32th': 32}

global_note = None
global_rest = None

def load_note_xml():
    """
    Funcao que carrega o arquivo xml referente a nota ou a pausa (rest).
    Essas variaveis sao usadas pela funcao new_note para a criacao de 
    notas e rests que serao geradas e adicionadas aos licks.
    """
    if global_note is None:
        f = open('files/xml/note.xml', 'r')
        global_note = etree.parse(f)
        f.close()

    if global_rest is None:
        f = open('files/xml/rest.xml', 'r')
        global_rest = etree.parse(f)
        f.close()


def new_note(note_type=0):
    """
    Funcao que cria uma nova nota ou pausa (rest) que sera usada para
    a construcao do lick.
    O parametro recebido precisa ser 0 (para criar uma nota), ou 1
    para criar uma pausa (rest).
    """
    if note_type == 0:
        if global_note is None:
            load_note_xml()
        return etree.parse(global_note)
    elif note_type == 1:
        if global_rest is None:
            load_note_xml()
        return etree.parse(global_rest)
    else:
        raise Exception('Parametro precisa ser 0 ou 1')


def fill_notes_matrix(tree, matrix):
    """
    Funcao que recebe uma elementTree que representa um lick e a matriz
    das notas e checa a ordem de transicao das notas. Resumindo, caso a
    nota y venha após a nota x incrementa a posicao matriz[x][y].
    """
    root = tree.getroot()
    notes = list(root.find('part').find('measure').iter('note'))

    for i in range(len(notes)-1):
        if notes[i].find('rest') is not None:
            line = 'REST'
        else:
            if notes[i].find('pitch') is not None:
                if notes[i].find('pitch').find('alter') is not None:
                    line = notes[i].find('pitch').find('step').text + '#'
                else:
                    line = notes[i].find('pitch').find('step').text
                    
        if notes[i+1].find('rest') is not None:
            column = 'REST'
        else:
            if notes[i+1].find('pitch') is not None:
                if notes[i+1].find('pitch').find('alter') is not None:
                    column = notes[i+1].find('pitch').find('step').text + '#'
                else:
                    column = notes[i+1].find('pitch').find('step').text

        matrix[note_dict[line]][note_dict[column]] += 1
        
        
def fill_tech_matrix(tree,matrix):
    """
    Funcao que preenche a matriz que representa as tecnicas usadas em cada
    nota. As linhas da matriz representam as tecnicas de guitarra na ordem
    do dicionario tech_dict e as colunas representam as notas na ordem da 
    escala cromática. OBS: A primeira coluna representa pausa ou rest e não
    deve ser levada em consideracao.
    """
    root = tree.getroot()
    notes = list(root.find('part').find('measure').iter('note'))
    
    for note in notes:
        if note.find('rest') is not None:
            continue
            
        slide = note.find('notations').find('slide')
        bend = note.find('notations').find('technical').find('bend')
        pulloff = note.find('notations').find('technical').find('pull-off')
        hammeron = note.find('notations').find('technical').find('hammer-on')
        
        if slide is not None:
            if slide.attrib.get('type') == 'start':
                if note.find('pitch').find('alter') is not None:
                    column = note.find('pitch').find('step').text + '#'
                else:
                    column = note.find('pitch').find('step').text
                matrix[tech_dict['slide']][note_dict[column]] += 1
        if bend is not None:
            bendrelease = note.find('notations').find('technical').find('bend').find('release')
            if bendrelease is not None:
                if note.find('pitch').find('alter') is not None:
                    column = note.find('pitch').find('step').text + '#'
                else:
                    column = note.find('pitch').find('step').text
                matrix[tech_dict['b-release']][note_dict[column]] += 1
            else:
                if note.find('pitch').find('alter') is not None:
                    column = note.find('pitch').find('step').text + '#'
                else:
                    column = note.find('pitch').find('step').text
                matrix[tech_dict['bend']][note_dict[column]] += 1
        if pulloff is not None:
            if pulloff.attrib.get('type') == 'start':
                if note.find('pitch').find('alter') is not None:
                    column = note.find('pitch').find('step').text + '#'
                else:
                    column = note.find('pitch').find('step').text
                matrix[tech_dict['pull']][note_dict[column]] += 1
        if hammeron is not None:
            if hammeron.attrib.get('type') == 'start':
                if note.find('pitch').find('alter') is not None:
                    column = note.find('pitch').find('step').text + '#'
                else:
                    column = note.find('pitch').find('step').text
                matrix[tech_dict['hammer']][note_dict[column]] += 1


def mount_notes_matrix():
    """
    Funcao que cria a matriz que vai armazenar os dados da transicao das
    notas do pool de licks. O preenchimento da matriz eh feito pela Funcao
    fill_notes_matrix.
    Basicamente eh criada uma matriz 13 x 13 (pausa, C, C#...A#, B) e feito
    o load do arquivo do lick que serao passados para a outra funcao.
    """
    matrix = []
    for i in range(13):
        matrix.append([0 for x in range(13)])
        
    for i in range(32):
        f = open('files/xml/%d.xml' %i, 'r')
        tree = etree.parse(f)
        fill_notes_matrix(tree,matrix)
        f.close()
        
    return matrix


def mount_tech_matrix():
    """
    Funcionamento similar a funcao mount_notes_matrix. A diferencao esta
    no fato da matriz criada ser 5 x 13 (tecnicas x notas). O load dos 
    arquivos eh feito da mesma forma e a funcao que recebe esses parametros
    eh a fill_tech_matrix.
    """
    matrix = []
    for i in range(5):
        matrix.append([0 for x in range(13)])
        
    for i in range(32):
        f = open('files/xml/%d.xml' %i, 'r')
        tree = etree.parse(f)
        fill_tech_matrix(tree,matrix)
        f.close()
        
    return matrix    
    

def get_prob_matrix(matrix):
    """
    Recebe uma matriz e monta a matriz de probabilidades Parte/Todo
    de cada linha.
    """
    prob_matrix = []
    for i in range(len(matrix)):
        if sum(matrix[i]) != 0:
            prob_matrix.append([round(x / float(sum(matrix[i])),3) for x in matrix[i]])
        else:
            if len(matrix) != 13:
                prob_matrix.append([round(1.0 / len(matrix[i]),3) for x in matrix[i]])
            else:
                prob_matrix.append(matrix[i])

    return prob_matrix


def fill_duration_matrix(tree,matrix):
    """
    Funcao que recebe um elementTree que representao xml das notas e monta 
    uma matriz que conta a relacao duracao -> duracao. Basicamente quantas vezes
    uma duracao ocorre apos a outra. A posicao da duracao na matrix segue a ordem
    definida no dicionario duration_index.
    """
    root = tree.getroot()
    notes = list(root.find('part').find('measure').iter('note'))

    for i in range(len(notes)-1):
        if notes[i].find('type') is not None:
            line = notes[i].find('type').text

        if notes[i+1].find('type') is not None:
            column = notes[i+1].find('type').text

        matrix[duration_index[line]][duration_index[column]] += 1


def mount_duration_matrix():
    """
    Funcionamento similar a funcao mount_notes_matrix. A diferenca esta
    no fato da matriz criada ser 7 x 7 que representa a duracao das notas, 
    qual duracao tem mais probabilidade  de vir apos uma dada. O load dos 
    arquivos eh feito da mesma forma e a funcao que recebe esses parametros
    eh a fill_duration_matrix.
    """
    matrix = []
    for i in range(6):
        matrix.append([0 for x in range(6)])

    for i in range(32):
        f = open('files/xml/%d.xml' %i, 'r')
        tree = etree.parse(f)
        fill_duration_matrix(tree,matrix)
        f.close()

    return matrix


def lick_duration(prob_durations):
    """
    Funcao que 'sorteia' com base nas probabilidades a duracao das notas dos licks.
    A primeira duracao é escolhida no random e as demais na probalilidade da
    sequencia com base na nota anterior.
    O parametro recebido é a matriz de probabilidades das duracoes das notas.
    """
    random.seed()
    first_duration = duration_values.keys()[random.randint(0,len(duration_values)-1)]
    duration = [first_duration]
    total = 4.0/duration_values[first_duration]
    attempt = 0
    while 1:
        if total == 4: break
        # print 'Total: ', total

        line = duration_index[duration[-1]]
        dice = random.randint(1,100)/100.0

        # print 'Line: ', line
        if 0 < dice <= prob_durations[line][0]:
            if total + (4.0/duration_values['whole']) <= 4:
                total += (4.0/duration_values['whole'])
                duration.append('whole')
                attempt = 0
        elif prob_durations[line][0] < dice <= sum(prob_durations[line][:2]):
            if total + (4.0/duration_values['half']) <= 4:
                total += (4.0/duration_values['half'])
                duration.append('half')
                attempt = 0
        elif sum(prob_durations[line][:2]) < dice <= sum(prob_durations[line][:3]):
            if total + (4.0/duration_values['quarter']) <= 4:
                total += (4.0/duration_values['quarter'])
                duration.append('quarter')
                attempt = 0
        elif sum(prob_durations[line][:3]) < dice <= sum(prob_durations[line][:4]):
            if total + (4.0/duration_values['eighth']) <= 4:
                total += (4.0/duration_values['eighth'])
                duration.append('eighth')
                attempt = 0
        elif sum(prob_durations[line][:4]) < dice <= sum(prob_durations[line][:5]):
            if total + (4.0/duration_values['16th']) <= 4:
                total += (4.0/duration_values['16th'])
                duration.append('16th')
                attempt = 0
        elif sum(prob_durations[line][:5]) < dice <= sum(prob_durations[line][:6]):
            if total + (4.0/duration_values['32th']) <= 4:
                total += (4.0/duration_values['32th'])
                duration.append('32th')
                attempt = 0
        # elif prob_durations[line][5] < dice <= (prob_durations[line][5] + prob_durations[line][6]):
        #     if total + (4.0/duration_values['64th']) <= 4:
        #         total += (4.0/duration_values['64th'])
        #         duration.append('64th')
        
        attempt += 1
        if attempt == 5:            
            d_removed = duration.pop(random.randint(0,len(duration)-1))
            total -= (4.0/duration_values[d_removed])
            attempt = 0
    
    return duration


def lick_notes(prob_notes, duration):
    random.seed()
    penta = ['C','D','E','G','A']
    notes = []
    first = penta[random.randint(0, len(penta)-1)]
    notes.append(first)

    print 'first', first
    # for line in prob_notes:
    #     print line

    while 1:
        line = note_dict[notes[-1]]
        dice = random.randint(1,100)/100.0

        print dice

        if 0 < dice <= prob_notes[line][0]:
            notes.append('REST')
        elif prob_notes[line][0] < dice <= sum(prob_notes[line][:2]):            
            notes.append('C')
        elif sum(prob_notes[line][:2]) < dice <= sum(prob_notes[line][:3]):
            notes.append('C#')
        elif sum(prob_notes[line][:3]) < dice <= sum(prob_notes[line][:4]):
            notes.append('D')
        elif sum(prob_notes[line][:4]) < dice <= sum(prob_notes[line][:5]):
            notes.append('D#')
        elif sum(prob_notes[line][:5]) < dice <= sum(prob_notes[line][:6]):
            notes.append('E')
        elif sum(prob_notes[line][:6]) < dice <= sum(prob_notes[line][:7]):
            notes.append('F')
        elif sum(prob_notes[line][:7]) < dice <= sum(prob_notes[line][:8]):
            notes.append('F#')
        elif sum(prob_notes[line][:8]) < dice <= sum(prob_notes[line][:9]):
            notes.append('G')
        elif sum(prob_notes[line][:9]) < dice <= sum(prob_notes[line][:10]):
            notes.append('G#')
        elif sum(prob_notes[line][:10]) < dice <= sum(prob_notes[line][:11]):
            notes.append('A')
        elif sum(prob_notes[line][:11]) < dice <= sum(prob_notes[line][:12]):
            notes.append('A#')
        elif sum(prob_notes[line][:12]) < dice <= sum(prob_notes[line]):
            notes.append('B')

        if len(notes) == len(duration):
            print duration
            print notes
            break




def create_lick(prob_notes, prob_durations):
    duration = lick_duration(prob_durations)
    # print duration
    lick = lick_notes(prob_notes, duration)


if __name__ == '__main__':
    notes_matrix = mount_notes_matrix()
    tech_matrix = mount_tech_matrix()
    duration_matrix = mount_duration_matrix()

    prob1 = get_prob_matrix(notes_matrix)
    prob2 = get_prob_matrix(duration_matrix)

    lick = create_lick(prob1,prob2)

    # print 'NOTES'
    # for line in notes_matrix:
    #     print line

    # print '\nTECHNIQUES'
    # for line in tech_matrix:
    #     print line

    # print '\nProbs-Notes'
    # for line in prob1:
    #     print line

    # print '\nDURATIONS'
    # for line in duration_matrix:
    #     print line

    # print '\nProbs-Durations'
    # for line in prob2:
    #     print line