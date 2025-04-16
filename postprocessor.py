#!/usr/bin/env python
#-*-coding: utf-8 -*-

from lxml import etree

import notes_handler


def tune_in_c(measure):
	# print 'TUNING IN C'
	notes = list(measure.iter('note'))
	for note in notes:
		if note.find('rest') is None and note.find('notehead') is None:
			if notes_handler.get_notetype_value(note) <= 4:
				if notes_handler.note_is_seventh_major('C', note):
					notes_handler.seventh_to_root_note('C', note)
				elif notes_handler.note_is_second_minor('C', note):
					notes_handler.second_minor_to_root_note('C', note)


def tune_in_f(measure):
	# print 'TUNING IN F'
	notes = list(measure.iter('note'))
	for note in notes:
		if note.find('rest') is None and note.find('notehead') is None:
			if notes_handler.get_notetype_value(note) <= 4:
				if notes_handler.note_is_seventh_major('F', note):
					notes_handler.seventh_to_root_note('F', note)


def tune_in_g(measure):
	# print 'TUNING IN G'
	notes = list(measure.iter('note'))
	for note in notes:
		if note.find('rest') is None and note.find('notehead') is None:
			if notes_handler.get_notetype_value(note) <= 4:
				if notes_handler.note_is_seventh_major('G', note):
					notes_handler.seventh_to_root_note('G', note)



def autotune(main_tree):
	print 'TUNING'
	root = main_tree.getroot()
	measures = list(root.iter('measure'))

	for i in range(len(measures)):
		if i <= 3: tune_in_c(measures[i])
		elif i > 3 and i <= 5: tune_in_f(measures[i])
		elif i > 5 and i <= 7: tune_in_c(measures[i])
		elif i == 8: tune_in_g(measures[i])
		elif i == 9: tune_in_f(measures[i])
		# elif i == 10: tune_in_c(measures[i])
		# elif i == 11: tune_in_g(measures[i])

	return main_tree


def main():
	pass

if __name__ == '__main__':
	main()