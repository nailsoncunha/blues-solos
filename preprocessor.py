#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys, os
from lxml import etree

import notes_handler, create_instance, mxml_handler


def check_coringa_index(tree):
	return notes_handler.check_coringa(tree)


def big_pause(tree1, tree2):
	plimit = 10
	# with open('%s/files/xml/%s/%d.xml' %(os.getcwd(), lfolder, i) ) as lick1:
	# 	tree1 = etree.parse(lick1)
	# with open('%s/files/xml/%s/%d.xml' %(os.getcwd(), lfolder, j) ) as lick2:
	# 	tree2 = etree.parse(lick2)

	if notes_handler.ends_with_pause(tree1) and notes_handler.starts_with_pause(tree2):
		psize = notes_handler.get_pause_size(tree1, 'end') + notes_handler.get_pause_size(tree2)
		# print psize 
		if psize <= plimit: # se a pausa for maior que duas seminimas
			return False
		else:
			return True
	elif notes_handler.ends_with_pause(tree1) and not notes_handler.starts_with_pause(tree2):
		psize = notes_handler.get_pause_size(tree1, 'end')
		# print psize 
		if psize <= plimit:
			return False
		else:
			return True
	elif not notes_handler.ends_with_pause(tree1) and notes_handler.starts_with_pause(tree2):
		psize = notes_handler.get_pause_size(tree2)
		# print psize 
		if psize <= plimit:
			return False
		else:
			return True

	return 0


def next_note_same_string(tree1, tree2):
	#print 'lick i: %d  ---  lick j: % d' %(i,j)
	# with open('%s/files/xml/%s/%d.xml' %(os.getcwd(), lfolder, i) ) as lick1:
	# 	tree1 = etree.parse(lick1)
	# with open('%s/files/xml/%s/%d.xml' %(os.getcwd(), lfolder, j) ) as lick2:
	# 	tree2 = etree.parse(lick2)

	if notes_handler.next_note_same_string(tree1, tree2):
		return True
	else:
		return False

	return 0


def previous_note_same_string(tree1, tree2):
	#print 'lick i: %d  ---  lick j: % d' %(i,j)
	# with open('%s/files/xml/%s/%d.xml' %(os.getcwd(), lfolder, i) ) as lick1:
	# 	tree1 = etree.parse(lick1)
	# with open('%s/files/xml/%s/%d.xml' %(os.getcwd(), lfolder, j) ) as lick2:
	# 	tree2 = etree.parse(lick2)

	if notes_handler.previous_note_same_string(tree1, tree2):
		return True
	else:
		return False

	return 0


def same_note_same_string(tree1, tree2):
	if notes_handler.same_note_same_string(tree1, tree2):
		return True
	else:
		return False

	return 0



def one_time_pause(lfolder, i, j, direction):
	with open('%s/files/xml/%s/%d.xml' %(os.getcwd(), lfolder, i) ) as lick1:
		tree1 = etree.parse(lick1)
	with open('%s/files/xml/%s/%d.xml' %(os.getcwd(), lfolder, j) ) as lick2:
		tree2 = etree.parse(lick2)

	if direction == 'previous':
		return notes_handler.previous_one_time_pause(tree1, tree2)
	elif direction == 'next':
		return notes_handler.next_one_time_pause(tree1, tree2)
	return 0



def starts_one_time_pause(tree):
	"""
    Acrescentei aqui quarter e o eighth para pausas validas.
    """
	return notes_handler.starts_one_time_pause(tree)


def ends_one_time_pause(tree):
	"""
    Acrescentei aqui quarter e o eighth para pausas validas.
    """
	return notes_handler.ends_one_time_pause(tree)


def starts_with_big_pause(tree):
	return notes_handler.starts_with_big_pause(tree)


def ends_with_big_pause(tree):
	return notes_handler.ends_with_big_pause(tree)



def main_full(lfolder, lick_dict, total_licks):

	licks_trees = mxml_handler.get_lick_trees(lfolder, lick_dict) #dicionario ligando um indice ao seu arquivo xml parseado em etree
	licks_trees = mxml_handler.get_turns_trees(licks_trees)
	# print licks_trees

	# print 'Qtde de licks na pasta %s' %lfolder 
	# print len( os.listdir( '%s/files/xml/%s' %(os.getcwd(), lfolder) ) )

	# total_licks = len( os.listdir( '%s/files/xml/%s' %(os.getcwd(), lfolder) ) )
	# print 'Licks: %d' %total_licks
	total_turns = len( os.listdir( '%s/files/xml/turnaround' %os.getcwd() ) )
	# print 'Turnarounds: %d' %total_turns
	matrix_size = total_licks + total_turns
	# print 'Matrix Size: ', matrix_size
	matrix_penal = [[100 for x in range(matrix_size+1)] for y in range(matrix_size+1)] # Inicializando a matriz com valor 103
	# matrix_penal[0] = [0 for x in range(matrix_size+1)] # Zerando a primeira linha

	cindex = open('cindex','w+b')
	rindex  = open('rindex','w+b')

	#Escreve os indices dos TAS nos arquivos
	taindex = open('taindex','w+b')
	for i in range(total_licks+1,total_licks+total_turns+1):
		taindex.write(str(i)+"\n")
	taindex.close()

	for i in range(matrix_size+1):
		coringa = None

		if i > 0 and i <= total_licks: # Zera a linha do dummy até chegar nos turnarounds
			coringa = check_coringa_index(licks_trees[i])
			if coringa:
				cindex.write(str(i)+"\n") # Aproveita o embalo e já escreve no arquivo quais são os indices dos licks coringa

			if starts_one_time_pause(licks_trees[i]) and not ends_with_big_pause(licks_trees[i]):
				rindex.write(str(i)+"\n")

			if ends_one_time_pause(licks_trees[i]) and not starts_with_big_pause(licks_trees[i]):
				rindex.write(str(i)+"\n")


		for j in range(matrix_size+1):
			if i == j:					# Zera a diagonal
				matrix_penal[i][j] = 0
			elif (i == 0 and j <= total_licks) or (j == 0): # Zera a primeira coluna
				matrix_penal[i][j] = 0
			elif j > total_licks: 	# Penalidade dos turnarounds para qualquer lick, exceto o dummy
				matrix_penal[i][j] = 100000

			if coringa and (i != j) and (i <= total_licks) and (j <= total_licks) and (i != 0) and (j != 0) : # Penalidade do coringa
				matrix_penal[i][j] -= 50
				matrix_penal[j][i] -= 50

			# if (i > 0 and i <= total_licks) and (j > 0 and j <= total_licks) and (i != j):
			if (i > 0) and (j > 0) and (i != j):
				if big_pause(licks_trees[i], licks_trees[j]): # Penalidade de Pausa gigante
					matrix_penal[i][j] += 25			

				if next_note_same_string(licks_trees[i], licks_trees[j]) or previous_note_same_string(licks_trees[i], licks_trees[j]) or same_note_same_string(licks_trees[i], licks_trees[j]):
					matrix_penal[i][j] -= 15

				if ends_one_time_pause(licks_trees[i]) and not notes_handler.starts_with_pause(licks_trees[j]):
					matrix_penal[i][j] -= 15
				
				if not notes_handler.ends_with_pause(licks_trees[i]) and starts_one_time_pause(licks_trees[j]):
					matrix_penal[i][j] -= 15
				
				if ends_one_time_pause(licks_trees[i]) and starts_one_time_pause(licks_trees[j]):
					matrix_penal[i][j] += 15


			# if i == 19 and j == 0: # Debug
			# 	matrix_penal[i][j] = 19

	cindex.close()

	create_instance.main(matrix_size+1, matrix_penal, total_licks, total_turns)

	# for line in matrix_penal:
	# 	print line

	return matrix_size, total_licks



def main_few(lfolder, lick_dict, total_licks):

	licks_trees = mxml_handler.get_lick_trees(lfolder, lick_dict) #dicionario ligando um indice ao seu arquivo xml parseado em etree
	licks_trees = mxml_handler.get_turns_trees(licks_trees)
	# print licks_trees

	# print 'Qtde de licks na pasta %s' %lfolder 
	# print len( os.listdir( '%s/files/xml/%s' %(os.getcwd(), lfolder) ) )

	# total_licks = len( os.listdir( '%s/files/xml/%s' %(os.getcwd(), lfolder) ) )
	# print 'Licks: %d' %total_licks
	total_turns = len( os.listdir( '%s/files/xml/turnaround' %os.getcwd() ) )
	# print 'Turnarounds: %d' %total_turns
	matrix_size = total_licks + total_turns
	# print 'Matrix Size: ', matrix_size
	matrix_penal = [[100 for x in range(matrix_size+1)] for y in range(matrix_size+1)] # Inicializando a matriz com valor 103
	# matrix_penal[0] = [0 for x in range(matrix_size+1)] # Zerando a primeira linha

	cindex = open('cindex','w+b')
	rindex  = open('rindex','w+b')

	#Escreve os indices dos TAS nos arquivos
	taindex = open('taindex','w+b')
	for i in range(total_licks+1,total_licks+total_turns+1):
		taindex.write(str(i)+"\n")
	taindex.close()

	for i in range(matrix_size+1):
		coringa = None

		if i > 0 and i <= total_licks: # Zera a linha do dummy até chegar nos turnarounds
			coringa = check_coringa_index(licks_trees[i])
			if coringa:
				cindex.write(str(i)+"\n") # Aproveita o embalo e já escreve no arquivo quais são os indices dos licks coringa

			if starts_one_time_pause(licks_trees[i]): # and not ends_with_big_pause(licks_trees[i]):
				rindex.write(str(i)+"\n")

			if ends_one_time_pause(licks_trees[i]): # and not starts_with_big_pause(licks_trees[i]):
				rindex.write(str(i)+"\n")


		for j in range(matrix_size+1):
			if i == j:					# Zera a diagonal
				matrix_penal[i][j] = 0
			elif (i == 0 and j <= total_licks) or (j == 0): # Zera a primeira coluna
				matrix_penal[i][j] = 0
			elif j > total_licks: 	# Penalidade dos turnarounds para qualquer lick, exceto o dummy
				matrix_penal[i][j] = 100000

			if coringa and (i != j) and (i <= total_licks) and (j <= total_licks) and (i != 0) and (j != 0) : # Penalidade do coringa
				matrix_penal[i][j] -= 50
				matrix_penal[j][i] -= 50

			# if (i > 0 and i <= total_licks) and (j > 0 and j <= total_licks) and (i != j):
			if (i > 0) and (j > 0) and (i != j):
				if big_pause(licks_trees[i], licks_trees[j]): # Penalidade de Pausa gigante
					matrix_penal[i][j] += 25			

				if next_note_same_string(licks_trees[i], licks_trees[j]) or previous_note_same_string(licks_trees[i], licks_trees[j]) or same_note_same_string(licks_trees[i], licks_trees[j]):
					matrix_penal[i][j] -= 15

				if ends_one_time_pause(licks_trees[i]) and not notes_handler.starts_with_pause(licks_trees[j]):
					matrix_penal[i][j] -= 15
				
				if not notes_handler.ends_with_pause(licks_trees[i]) and starts_one_time_pause(licks_trees[j]):
					matrix_penal[i][j] -= 15
				
				if ends_one_time_pause(licks_trees[i]) and starts_one_time_pause(licks_trees[j]):
					matrix_penal[i][j] += 15


			# if i == 19 and j == 0: # Debug
			# 	matrix_penal[i][j] = 19

	cindex.close()

	create_instance.main(matrix_size+1, matrix_penal, total_licks, total_turns)

	# for line in matrix_penal:
	# 	print line

	return matrix_size, total_licks


if __name__ == '__main__':
	if len(sys.argv) > 1:		
		main(sys.argv[1])
	# print 'Qtde de licks na pasta %s' %lfolder 
	# print len( os.listdir( '%s/files/xml/%s' %(os.getcwd(), lfolder) ) )		
	else:
		print 'Speed? s -> slow, m -> moderate, f -> fast'