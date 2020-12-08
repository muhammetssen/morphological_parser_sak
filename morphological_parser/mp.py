
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Hasim Sak
#Description: An example python script to use the stochastic morphological parser for Turkish.

import sys
import re
import morphological_parser.TurkishMorphology as TurkishMorphology
import morphological_parser.md as md
import subprocess
import logging
import os
import atexit
import asyncio
import time

try:
    import importlib.resources as pkg_resources
except ImportError:
    import importlib_resources as pkg_resources

with pkg_resources.path(__package__, "turkish.fst") as p:
    fst_path = str(p.resolve())
    model_path = str(p.resolve().parent / "model.txt")


DEBUG = False 
log_level = logging.DEBUG if DEBUG else logging.INFO
logging.basicConfig(stream=sys.stderr, level=log_level)



def init_fst():
    logging.debug("Loading FST...")
    TurkishMorphology.load_lexicon(fst_path)

"""
Initialize everything
"""
def init():
    init_fst()
    md.init(model_path)

def cleanup():
    pass

"""
Returns list of lists: where each list is morphological parses of a sentence
"""
def parse_lines(lines):
    logging.debug("Parsing...")
    parsed_text = ""
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

def evaluate(text):
    lines = [line for line in text.split("\n") if line]
    parsed_text = parse_lines(lines)
    result = md.disamb(parsed_text)
    return result

def debug():
    while True:
        inp = input("INPUT: ")
        if inp == "q":
            break
        else:
            print(evaluate(inp))

# init if import
init()

def clear():
    cleanup()
atexit.register(clear)


if __name__ == '__main__':
    debug()
