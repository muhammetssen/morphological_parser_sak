#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Hasim Sak
#Description: An example python script to use the stochastic morphological parser for Turkish.

import sys
import re
import TurkishMorphology

def init():
	TurkishMorphology.load_lexicon('turkish.fst')

"""
Returns list of lists: where each list is morphological parses of a sentence
"""
def parse_lines(text):
	parsed_text = ""
	lines = [x for x in text.strip().split("\n") if x]
	for line in lines:
		parsed_text += "<S> <S>+BSTag\n" 
		line = line.rstrip()
		words = re.split('\s+', line)
		for w in words:
			parses = TurkishMorphology.parse(w)
			if not parses:
				parsed_text += w + " " + w + "[Unknown]\n"
				continue
			parsed_text += w
			for p in parses: #There may be more than one possible morphological analyses for a word
				(parse, neglogprob) = p #An estimated negative log probability for a morphological analysis is also returned
				parsed_text += " " + parse
			parsed_text += "\n"
		parsed_text += "</S> </S>+ESTag\n"
	return parsed_text

# Test
if __name__ == '__main__':
	init()
	print(parse_lines("şekerlerinin"), end="")
