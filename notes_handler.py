#!/usr/bin/env python
#-*-coding: utf-8 -*-


import sys, os

from lxml import etree

scale = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']

notetypes = {
    'whole': 1,
    'half': 2,
    'quarter': 4,
    'eighth': 8,
    '16th': 16,
    '32th': 32
}


class CommonEqualityMixin(object):
    """
    Classe criada para ser extendida pelas classes Note, Rest e Chord de modo a
    facilitar a comparacao entre os objetos.
    """
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class Note(CommonEqualityMixin):
    """
    Classe que representa uma nota dentro de um lick ou quarto de lick.
    """
    def __init__(self, step, fret, string_number, notetype, technical=None):
        self.step = step
        self.notetype = notetype
        self.technical = technical
        self.fret = fret
        self.string_number = string_number

    def __str__(self):
        return '%s' %self.step


class Rest(CommonEqualityMixin):
    """
    Classe que representa uma pausa (rest) dentro de um lick ou quarto de lick.
    """
    def __init__(self, notetype):
        self.notetype = notetype


class Chord(CommonEqualityMixin):
    """
    Classe que representa um acorde (chord) dentro de um lick ou quarto de lick.
    Possui uma lista de notas.
    """
    def __init__(self):
        self.notes = []

    def add_note(self, note):
        self.notes.append(note)
        

def get_key_chromatic_scale(key):
    """
    Funcao que gera a escala cromatica de uma determinada nota.
    key -> string que representa a nota que sera a tonica da escala.
    Retorna a escala gerada
    """
    key = key.upper()
    try:
        return scale[scale.index(key):] + scale[:scale.index(key)]
    except ValueError:
        print "Nota nao encontrada.\nUsar notas naturais ou com '#': (Lembre-se que E e B não possuem #)"
        print "Ex: 'C','C#','D','D#','E','F','F#','G','G#','A','A#','B'"


def remove_string_fret(note):
    if note.find('notations') is not None:
        if note.find('notations').find('technical') is not None:
            note.find('notations').find('technical').remove(note.find('notations').find('technical').find('string'))
            note.find('notations').find('technical').remove(note.find('notations').find('technical').find('fret'))
    return note


def get_notetype_value(note):
    if note.find('type') is not None:
        return notetypes.get(note.find('type'))
    else: return 128


def note_is_second_minor(root_note, note):
    chromatic_scale = get_key_chromatic_scale(root_note)
    note_step = note.find('pitch').find('step').text
    if note.find('pitch').find('alter') is not None:
        note_step += '#'

    if note_step == chromatic_scale[1]:
        return True
    else:
        return False

    return 0



def second_minor_to_root_note(root_note, note):
    if '#' not in root_note and note.find('pitch').find('alter') is not None:
        note.find('pitch').find('step').text = root_note.upper()
        note.find('pitch').remove(note.find('pitch').find('alter'))
        note.find('notations').find('technical').find('fret').text = str( int(note.find('notations').find('technical').find('fret').text) - 1 ) 
    elif '#' in root_note and note.find('pitch').find('alter') is not None:
        note.find('pitch').find('step').text = root_note[0].upper()
        note.find('notations').find('technical').find('fret').text = str( int(note.find('notations').find('technical').find('fret').text) - 1 ) 
    elif '#' not in root_note and note.find('pitch').find('alter') is None:
        note.find('pitch').find('step').text = root_note.upper()
        note.find('notations').find('technical').find('fret').text = str( int(note.find('notations').find('technical').find('fret').text) - 1 )
    elif '#' in root_note and note.find('pitch').find('alter') is None:
        note.find('pitch').find('step').text = root_note[0].upper()
        alter = etree.Element('alter')
        alter.text = 1
        note.find('pitch').find('step').addnext(alter)
        note.find('notations').find('technical').find('fret').text = str( int(note.find('notations').find('technical').find('fret').text) - 1 )



def note_is_seventh_major(root_note, note):
    chromatic_scale = get_key_chromatic_scale(root_note)
    note_step = note.find('pitch').find('step').text
    if note.find('pitch').find('alter') is not None:
        note_step += '#'

    if note_step == chromatic_scale[-1]:
        return True
    else:
        return False

    return 0


def seventh_to_root_note(root_note, note):
    if '#' not in root_note and note.find('pitch').find('alter') is not None:
        note.find('pitch').find('step').text = root_note.upper()
        note.find('pitch').remove(note.find('pitch').find('alter'))
        note.find('notations').find('technical').find('fret').text = str( int(note.find('notations').find('technical').find('fret').text) + 1 ) 
    elif '#' in root_note and note.find('pitch').find('alter') is not None:
        note.find('pitch').find('step').text = root_note[0].upper()
        note.find('notations').find('technical').find('fret').text = str( int(note.find('notations').find('technical').find('fret').text) + 1 ) 
    elif '#' not in root_note and note.find('pitch').find('alter') is None:
        note.find('pitch').find('step').text = root_note.upper()
        note.find('notations').find('technical').find('fret').text = str( int(note.find('notations').find('technical').find('fret').text) + 1 )
    elif '#' in root_note and note.find('pitch').find('alter') is None:
        note.find('pitch').find('step').text = root_note[0].upper()
        alter = etree.Element('alter')
        alter.text = 1
        note.find('pitch').find('step').addnext(alter)
        note.find('notations').find('technical').find('fret').text = str( int(note.find('notations').find('technical').find('fret').text) + 1 )



def transpose_measure(from_key, to_key, measure):
    """
    Funcao que executa a segunda etapa do transpose. Transpoe cada
    compasso recebido para o tom indicado.
    from_key -> lista com chromatic scale da tonalidade original
    to_key -> lista com chromatic scale da nova tonalidade
    measure ->  lxml.Element que representa o compasso a ser transposto
    """
    notes = list(measure.iter('note'))
    for note in notes:
        if note.find('pitch') is not None:
            if note.find('pitch').find('step') is not None:
                n = note.find('pitch').find('step').text
                if note.find('pitch').find('alter') is not None:
                    n += '#'
                    note_index = from_key.index(n.upper())
                    new_note = to_key[note_index]
                    if '#' in new_note:
                        note.find('pitch').find('step').text = new_note[0]
                    else:
                        note.find('pitch').find('step').text = new_note[0]
                        note.find('pitch').remove(note.find('pitch').find('alter'))
                else:
                    note_index = from_key.index(n.upper())
                    new_note = to_key[note_index]
                    if '#' in new_note:
                        alter = etree.Element('alter')
                        alter.text = '1'
                        note.find('pitch').find('step').text = new_note[0]
                        note.find('pitch').insert(1,alter)
                    else:
                        note.find('pitch').find('step').text = new_note[0]
            note = remove_string_fret(note)
    return measure
                    

def transpose(from_key, to_key, lick_tree):
    """
    Funcao que realiza a primeira etapa do transpose. Separa e envia um
    compasso de cada vez para ser transposto.
    from_key -> string que indica o tom original do lick
    to_key -> string que indica o tom ao qual o lick sera transposto
    lick_tree -> lxml.Element que representa o lick
    """
    from_key = get_key_chromatic_scale(from_key)
    to_key = get_key_chromatic_scale(to_key)
    
    lick_root = lick_tree.getroot()
    measures = list(lick_root.iter('measure'))
    for mea in measures:
        mea = transpose_measure(from_key, to_key, mea)
    
    return lick_tree
    

def print_notes(xml_tree):
    root = xml_tree.getroot()
    measures = list(root.iter('measure'))
    notes = []
    for i in range(len(measures)):
        print 'Measure %d:' %i
        for note in list(measures[i].iter('note')):
            if note.find('pitch') is not None:
                if note.find('pitch').find('alter') is not None:
                    notes.append(note.find('pitch').find('step').text + '#')
                else:
                    notes.append(note.find('pitch').find('step').text)
        print notes
    print '\n'
        

#APENAS PARA TESTE - EXCLUIR DEPOIS
def print_notes2(root):
    measures = list(root.iter('measure'))
    notes = []
    for i in range(len(measures)):
        print 'Measure %d:' %i
        for note in list(measures[i].iter('note')):
            if note.find('pitch') is not None:
                if note.find('pitch').find('alter') is not None:
                    notes.append(note.find('pitch').find('step').text + '#')
                else:
                    notes.append(note.find('pitch').find('step').text)
        print notes
    print '\n'


def starts_with_pause(lick):
    """
    Funcao que recebe como parametro um etree Element que representa um lick e 
    checa se o mesmo comeca com uma pausa. Retorna True se uma pausa for encontrada
    na primeira posicao e False caso contrario.
    """
    root = lick.getroot()
    notes = list(root.find('part').find('measure').iter('note'))

    if notes[0].find('rest') is not None:
        return True
    else:
        return False


def ends_with_pause(lick):
    """
    Funcao que recebe como parametro um etree Element que representa um lick e 
    checa se o mesmo termina com uma pausa. Retorna True se uma pausa for encontrada
    na ultima posicao e False caso contrario.
    """
    root = lick.getroot()
    notes = list(root.find('part').find('measure').iter('note'))

    if notes[-1].find('rest') is not None:
        return True
    else:
        return False


def get_pause_size(lick, position='begin'):
    """
    Funcao que calcula a duracao da pausa no inicio ou no final do lick.
    Recebe como parametro um etree Element que representa o lick, e uma string
    que representa em que posicao o duracao da pausa deve ser calculada, no inicio
    ou no fim.
    Retorna o tamanho da duracao da pausa.
    """
    duration = 0
    root = lick.getroot()
    notes = list(root.find('part').find('measure').iter('note'))
    if position == 'end':
        notes.reverse()

    for note in notes:
        if note.find('rest') is not None:
            duration += int(note.find('duration').text)
        else:
            break

    return duration


def create_note(note):
    """
    Função que recebe um XMLElement da tag <note> de um MusicXML e retorna um
    objeto da classe Note.
    """
    if note.find('notehead') is not None:
        step  = 'x'
        fret = None
    else:
        step  = note.find('pitch').find('step').text            
        fret = note.find('notations').find('technical').find('fret').text
    notetype = note.find('type').text
    string_number = note.find('notations').find('technical').find('string').text
    # technical = note.find('notations').find('technical').find('fret').getnext()
    
    return Note(step, fret, string_number, notetype)


def is_chord(note):
    """
    Funcao que retorna true caso encontre a tag <chord> dentro de um XMLElement
    da tag <note>. Indicando que a nota é parte de um acorde.
    """
    if note.find('chord') is not None:
        return True
    else:
        return False


def note_is_grace(note):
    """
    Funcao que retorna true caso encontre a tag <grace> dentro de um XMLElement
    da tag <note>. Indicando que a nota é uma apogiatura.
    """
    if note.find('grace') is not None:
        return True
    else:
        return False



def next_note_same_string(lick1, lick2):
    root1 = lick1.getroot()
    root2 = lick2.getroot()

    notes_lick1 = list(root1.find('part').find('measure').iter('note'))
    notes_lick2 = list(root2.find('part').find('measure').iter('note'))

    if note_is_grace(notes_lick2[0]): # Se a primeira nota do lick 2 é apoggiatura, pegue a proxima nota
        note2_index = 1
    else:
        note2_index = 0

    if notes_lick1[-1].find('rest') is not None or notes_lick2[note2_index].find('rest') is not None: # Se alguma das duas for pausa
        return False

    if notes_lick1[-1].find('notehead') is not None or notes_lick2[note2_index].find('notehead') is not None: # Se alguma das duas nota morta
        return False

    if notes_lick1[-1].find('notations').find('technical').find('string') is None: # Se não é pausa ou outra técnica que não marca uma corda
        return False
    else:
        if notes_lick2[note2_index].find('notations').find('technical').find('string') is None: # Se não é pausa ou outra técnica que não marca uma corda
            return False
        else:
            # Se as cordas são diferentes
            if notes_lick1[-1].find('notations').find('technical').find('string').text != notes_lick2[note2_index].find('notations').find('technical').find('string').text:
                return False
            else:
                fret1 = int(notes_lick1[-1].find('notations').find('technical').find('fret').text)
                fret2 = int(notes_lick2[note2_index].find('notations').find('technical').find('fret').text)

                if (fret2 == (fret1 + 3)) or fret2 == (fret1 + 2):
                    return True
                else:
                    return False
    return 0



def same_note_same_string(lick1, lick2):
    root1 = lick1.getroot()
    root2 = lick2.getroot()

    notes_lick1 = list(root1.find('part').find('measure').iter('note'))
    notes_lick2 = list(root2.find('part').find('measure').iter('note'))

    if note_is_grace(notes_lick2[0]): # Se a primeira nota do lick 2 é apoggiatura, pegue a proxima nota
        note2_index = 1
    else:
        note2_index = 0

    if notes_lick1[-1].find('rest') is not None or notes_lick2[note2_index].find('rest') is not None: # Se alguma das duas for pausa
        return False

    if notes_lick1[-1].find('notehead') is not None or notes_lick2[note2_index].find('notehead') is not None: # Se alguma das duas nota morta
        return False

    if notes_lick1[-1].find('notations').find('technical').find('string') is None: # Se não é pausa ou outra técnica que não marca uma corda
        return False
    else:
        if notes_lick2[note2_index].find('notations').find('technical').find('string') is None: # Se não é pausa ou outra técnica que não marca uma corda
            return False
        else:
            # Se as cordas são diferentes
            if notes_lick1[-1].find('notations').find('technical').find('string').text != notes_lick2[note2_index].find('notations').find('technical').find('string').text:
                return False
            else:
                fret1 = int(notes_lick1[-1].find('notations').find('technical').find('fret').text)
                fret2 = int(notes_lick2[note2_index].find('notations').find('technical').find('fret').text)

                if fret2 == fret1:
                    return True
                else:
                    return False
    return 0



def previous_note_same_string(lick1, lick2):
    root1 = lick1.getroot()
    root2 = lick2.getroot()

    notes_lick1 = list(root1.find('part').find('measure').iter('note'))
    notes_lick2 = list(root2.find('part').find('measure').iter('note'))

    if note_is_grace(notes_lick2[0]): # Se a primeira nota do lick 2 é apoggiatura, pegue a proxima nota
        note2_index = 1
    else:
        note2_index = 0

    if notes_lick1[-1].find('rest') is not None or notes_lick2[note2_index].find('rest') is not None: # Se alguma das duas for pausa
        return False

    if notes_lick1[-1].find('notehead') is not None or notes_lick2[note2_index].find('notehead') is not None: # Se alguma das duas nota morta
        return False

    if notes_lick1[-1].find('notations').find('technical').find('string') is None: # Se não é pausa ou outra técnica que não marca uma corda
        return False
    else:
        if notes_lick2[note2_index].find('notations').find('technical').find('string') is None: # Se não é pausa ou outra técnica que não marca uma corda
            return False
        else:
            # Se as cordas são diferentes
            if notes_lick1[-1].find('notations').find('technical').find('string').text != notes_lick2[note2_index].find('notations').find('technical').find('string').text:
                return False
            else:
                fret1 = int(notes_lick1[-1].find('notations').find('technical').find('fret').text)
                fret2 = int(notes_lick2[note2_index].find('notations').find('technical').find('fret').text)

                if (fret2 == (fret1 - 3)) or fret2 == (fret1 - 2):
                    return True
                else:
                    return False
    return 0


def next_one_time_pause(lick1, lick2):
    root1 = lick1.getroot()
    root2 = lick2.getroot()

    if ends_with_pause(lick1) or not starts_with_pause(lick2):
        return False
    else:
        notes = list(root2.find('part').find('measure').iter('note'))
        if notes[0].find('type').text == 'quarter' and notes[1].find('rest') is None:
            return True
        else:
            return False

    return 0



def previous_one_time_pause(lick1, lick2):
    root1 = lick1.getroot()
    root2 = lick2.getroot()

    if not ends_with_pause(lick1) or starts_with_pause(lick2):
        return False
    else:
        notes = list(root1.find('part').find('measure').iter('note'))
        if notes[-1].find('type').text == 'quarter' and notes[-2].find('rest') is None:
            return True
        else:
            return False

    return 0



def starts_one_time_pause(lick):
    """
    Acrescentei aqui quarter e o eighth para pausas validas.
    """
    root = lick.getroot()
    notes = list(root.find('part').find('measure').iter('note'))

    if notes[0].find('rest') is None:
        return False

    if notes[0].find('type').text == 'quarter' and notes[1].find('rest') is None:
        return True
    elif notes[0].find('type').text == 'eighth' and notes[1].find('rest') is None:
        return True

    return 0


def ends_one_time_pause(lick):
    root = lick.getroot()
    notes = list(root.find('part').find('measure').iter('note'))

    if notes[-1].find('rest') is None:
        return False

    if notes[-1].find('type').text == 'quarter' and notes[-2].find('rest') is None:
        return True
    elif notes[-1].find('type').text == 'eighth' and notes[-2].find('rest') is None:
        return True

    return 0


def starts_with_big_pause(lick):
    root = lick.getroot()
    notes = list(root.find('part').find('measure').iter('note'))

    if not starts_with_pause(lick):
        return False

    if notes[1].find('rest') is not None:
        return True

    return 0



def ends_with_big_pause(lick):
    root = lick.getroot()
    notes = list(root.find('part').find('measure').iter('note'))

    if not ends_with_pause(lick):
        return False

    if notes[-2].find('rest') is not None:
        return True

    return 0



def lick_quarter(lick):
    """
    Codigo que recebe um lick e retorna o mesmo dividido em quatro tempos. Cada tempo equivale a uma lista de notas
    que o preenche.
    Lança uma Exception caso o lick tenha notas que durem mais de um tempo, o que impede de o split ser de 4 tempos.
    """
    root = lick.getroot()
    notes = list(root.find('part').find('measure').iter('note'))

    if len(notes) < 4 : raise Exception('O lick possui menos de 4 notas')

    quarter_bar = []
    full_bar = []
    bar_duration = 0.0

    for note in notes:

        if note_is_grace(note):
            continue

        if notetypes.get(note.find('type').text) < 4:
            raise Exception('Menos de 4 itens no split')

        if note.find('rest') is None:
              
            if not is_chord(note) and note.getnext() is not None and is_chord(note.getnext()):
                new_chord = Chord()
                new_note = create_note(note)
                new_chord.add_note(new_note)
                continue
            elif is_chord(note) and note.getnext() is not None and is_chord(note.getnext()):
                new_note = create_note(note)
                new_chord.add_note(new_note)
                continue
            elif is_chord(note) and note.getnext() is not None and not is_chord(note.getnext()):
                new_note = create_note(note)
                new_chord.add_note(new_note)
            else:
                new_note = create_note(note)
                

            if note.find('time-modification') is not None:
                note_duration = (notetypes.get(new_note.notetype) * 4.0) / 3.0
                bar_duration += (4.0 / note_duration)

                if bar_duration == 1.0625 or bar_duration == 1.125:
                    if is_chord(note):
                        quarter_bar.append(new_chord)
                    else:
                        quarter_bar.append(new_note)
                    full_bar.append(quarter_bar)
                    bar_duration = 0
                    # print quarter_bar
                    quarter_bar = []
                    continue
                else:
                    if is_chord(note):
                        quarter_bar.append(new_chord)
                    else:
                        quarter_bar.append(new_note)
                    continue


            if note.find('dot') is not None:
                bar_duration += (4.0 / notetypes.get(new_note.notetype))
                bar_duration += (4.0 / (notetypes.get(new_note.notetype)*2) )

            else:
                bar_duration += ( 4.0 / notetypes.get(new_note.notetype) )

            if bar_duration == 1:
                if is_chord(note):
                    quarter_bar.append(new_chord)
                else:
                    quarter_bar.append(new_note)
                full_bar.append(quarter_bar)
                bar_duration = 0
                # print quarter_bar
                quarter_bar = []
            else:
                if is_chord(note):
                    quarter_bar.append(new_chord)
                else:
                    quarter_bar.append(new_note)
                
        else:
            notetype = note.find('type').text
            # bar_duration += (4.0 / notetypes.get(notetype))
            new_rest = Rest(notetype)

            if note.find('time-modification') is not None:
                note_duration = (notetypes.get(notetype) * 4.0) / 3.0
                bar_duration += (4.0 / note_duration)

                if bar_duration == 1.0625 or bar_duration == 1.125:
                    quarter_bar.append(new_rest)
                    full_bar.append(quarter_bar)
                    bar_duration = 0
                    # print quarter_bar
                    quarter_bar = []
                    continue
                else:
                    quarter_bar.append(new_rest)
                    continue
            else:
                bar_duration += (4.0 / notetypes.get(notetype))

            if bar_duration == 1:
                quarter_bar.append(new_rest)
                full_bar.append(quarter_bar)
                bar_duration = 0
                # print quarter_bar
                quarter_bar = []
            else:
                quarter_bar.append(new_rest)
    # print full_bar
    return full_bar


def compare_quarter_pairs(lquarter):
    """
    Funcao que pega um lick dividido em quartos e compara os quartos em pares,
    primeiro com o terceiro e segundo com o quarto. Retorna true caso sejam iguais.
    """
    if len(lquarter) == 4:
        if len(lquarter[0]) == len(lquarter[2]) and len(lquarter[1]) == len(lquarter[3]):
            # print '(Pairs)'
            return lquarter[0] == lquarter[2] and lquarter[1] == lquarter[3]
        else: return False


def compare_quarters(lquarter):
    """
    Funcao que pega um lick dividido em quartos e compara os quartos da seguinte forma.
    Primeiro com o segundo e primeiro com o terceiro. Retorna true caso seja igual. Caso
    essa comparacao seja falsa é feita uma segunda comparacao de outra forma.

    Segunda forma: segundo com terceiro e segundo com o quarto. Retorna true caso sejam
    iguais.
    """
    if len(lquarter) >= 3:
        if len(lquarter[0]) == len(lquarter[1]) and len(lquarter[0]) == len(lquarter[2]):
            if lquarter[0] == lquarter[1] and lquarter[0] == lquarter[2]:
                return lquarter[0] == lquarter[1] and lquarter[0] == lquarter[2]
            elif lquarter[1] == lquarter[2] and lquarter[1] == lquarter[3]:
                return lquarter[1] == lquarter[2] and lquarter[1] == lquarter[3]
        else:
            return compare_quarter_pairs(lquarter)
    else:
        return False


def check_coringa(lick):
    try:
        lquarter = lick_quarter(lick)
        if lquarter:
            return compare_quarters(lquarter)
        else:
            return False
    except Exception, e:
        # print e
        return False


def main(choice):    
    if choice == 1:
        xmls = os.listdir( '%s/files/xml' %os.getcwd() )
        print 'Licks que começam com pause'
        for xmlname in xmls:
            if not os.path.isfile( '%s/files/xml/%s' %(os.getcwd(), xmlname) ):
                continue
            tree = etree.parse( open('%s/files/xml/%s' %(os.getcwd(), xmlname)) )
            result = starts_with_pause(tree)
            if result:
                pause_duration = get_pause_size(tree,'begin')
                print 'Lick %s -> Duração da pausa = %d' %(xmlname, pause_duration)
    elif choice == 2:
        xmls = os.listdir( '%s/files/xml' %os.getcwd() )
        print 'Licks que terminam com pause'
        for xmlname in xmls:
            if not os.path.isfile( '%s/files/xml/%s' %(os.getcwd(), xmlname) ):
                continue
            tree = etree.parse( open('%s/files/xml/%s' %(os.getcwd(), xmlname)) )
            result = ends_with_pause(tree)
            if result:
                pause_duration = get_pause_size(tree, 'end')
                print 'Lick %s -> Duração da pausa = %d' %(xmlname, pause_duration)
    elif choice == 3:
        xmls = os.listdir( '%s/files/xml' %os.getcwd() )
        print 'Check de licks coringa'
        for xmlname in xmls:
            if not os.path.isfile( '%s/files/xml/%s' %(os.getcwd(), xmlname) ):
                continue
            tree = etree.parse( open('%s/files/xml/%s' %(os.getcwd(), xmlname)) )
            print xmlname
            result = check_coringa(tree)
            # raw_input("PRESS ENTER TO CONTINUE.")
            # if not result:
            #     print 'Lick %s não pode ser coringa!' %xmlname



if __name__ == "__main__":
    main(int(sys.argv[1]))

    # instance = int(sys.argv[1])
    # f = open('files/xml/%s.xml' %instance,'r+b')
    # main_tree = etree.parse(f)
    
    # print get_key_chromatic_scale('C')
    # print get_key_chromatic_scale('D')
    
    # print 'Tom original:'
    # print_notes(main_tree)
    
    # main_tree = transpose('c', 'd', main_tree)
    
    # print "\n Transposto:"
    # print_notes(main_tree)
    
    
