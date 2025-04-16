#!/usr/bin/env python
#-*-coding: utf-8 -*-

from lxml import etree

import sys, os

DROPBOX_PATH = "/home/nailson/Dropbox/My Documents/Projeto-Mestrado/Pesquisa operacional/licks-temp/Split"
SLOW_FOLDER = "/home/nailson/projects/solos-research/files/xml/slow"
MODERATE_FOLDER = "/home/nailson/projects/solos-research/files/xml/moderate"
FAST_FOLDER = "/home/nailson/projects/solos-research/files/xml/fast"

xml_attributes = """
<attributes><divisions>1</divisions>
				<key><fifths>0</fifths>
					<mode>major</mode>
				</key>
				<time><beats>4</beats>
					<beat-type>4</beat-type>
				</time>
				<clef><sign>TAB</sign>
					<line>5</line>
				</clef>
				<staff-details><staff-lines>6</staff-lines>
					<staff-tuning line="6"><tuning-step>E</tuning-step>
						<tuning-octave>5</tuning-octave>
					</staff-tuning>
					<staff-tuning line="5"><tuning-step>B</tuning-step>
						<tuning-octave>4</tuning-octave>
					</staff-tuning>
					<staff-tuning line="4"><tuning-step>G</tuning-step>
						<tuning-octave>4</tuning-octave>
					</staff-tuning>
					<staff-tuning line="3"><tuning-step>D</tuning-step>
						<tuning-octave>4</tuning-octave>
					</staff-tuning>
					<staff-tuning line="2"><tuning-step>A</tuning-step>
						<tuning-octave>3</tuning-octave>
					</staff-tuning>
					<staff-tuning line="1"><tuning-step>E</tuning-step>
						<tuning-octave>3</tuning-octave>
					</staff-tuning>
				</staff-details>
			</attributes>
"""

xml_sound = '<sound pan="8" tempo="120"></sound>'
xml_barline1 = '<barline location="left"><bar-style>heavy-light</bar-style></barline>'
total_generated = 0


def save_new_lick(bltree, number, lfolder, turnaround=False):
	global total_generated
	#out_file = open('%s/%d.xml' %(DROPBOX_PATH, number),'w+b')
	if lfolder == 'slow':
		out_file = open('%s/%d.xml' %(SLOW_FOLDER, number),'w+b')
	elif lfolder == 'moderate':
		out_file = open('%s/%d.xml' %(MODERATE_FOLDER, number),'w+b')
	elif lfolder == 'fast':
		out_file = open('%s/%d.xml' %(FAST_FOLDER, number),'w+b')
	out_file.write(etree.tostring(bltree))
	out_file.close()
	total_generated += 1


def get_blank_lick():
	blank_lick = open('%s/files/xml/utils/blanklick.xml' %os.getcwd())
	bltree = etree.parse(blank_lick)
	blank_lick.close()
	return bltree


def main(lspeed, verbose=False):
	start=1

	if lspeed == 's' or lspeed == 'S':
		lfolder = 'slow'
	elif lspeed == 'm' or lspeed == 'M':
		lfolder = 'moderate'
	elif lspeed == 'f' or lspeed == 'F':
		lfolder = 'fast'


	xmls = os.listdir( '%s/files/xml/%s' %(os.getcwd(), lfolder) )
	for filename in xmls:
		if verbose:
			print 'Spliting file %s' %filename

		current_lick = etree.parse( open('%s/files/xml/%s/%s' %(os.getcwd(), lfolder,filename) ) )
		measures = list(current_lick.iter('measure') )

		for mea in measures:
			bltree = get_blank_lick()
			blroot = bltree.getroot()
			blank_part = blroot.find('part')

			if mea.find('attributes') is not None:
				blank_part.append(mea)
			else:
				mea.insert(0,etree.fromstring(xml_attributes))
				mea.insert(1,etree.fromstring(xml_sound))
				mea.insert(2,etree.fromstring(xml_barline1))
				mea.set("number","1")
				blank_part.append(mea)
			
			if 'TURNAROUND' in filename:
				save_new_lick(bltree, start, lfolder, True)
			else:
				save_new_lick(bltree, start, lfolder)
			start += 1



if __name__ == '__main__':
	if len(sys.argv) < 2:
		print 'Argumentos: S, M ou F pra os licks e v para verbose'
		sys.exit(0)

	try:
		if len(sys.argv) > 2:
			if sys.argv[2]=='v':
				# main(int(sys.argv[1]), True)
				main(sys.argv[1], True)
			else:
				# main(int(sys.argv[1]))
				main(sys.argv[1])
		else:
			# main(int(sys.argv[1]))
			main(sys.argv[1])
	except ValueError:
		print 'Tem certeza que passou um numero como argumento?'
		sys.exit(0)
	
	#print os.listdir( '%s/files/licks-orig' %os.getcwd() )
	print 'Concluído, licks gerados = %d' %total_generated