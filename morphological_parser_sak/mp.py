#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Hasim Sak
#Description: An example python script to use the stochastic morphological parser for Turkish.

import sys
import re
import TurkishMorphology
import subprocess
import flask
import logging
import os
from websocket import create_connection

"""
    This is supposed to run in a container. The port selection is arbitrary
        since there is not much of a process running 
"""
DISAMB_ADDR = "127.0.0.1"
DISAMB_PORT = 34215
perl_script = "md.pl"
perl_proc = None
ws = None
DEBUG = True # TODO

log_level = logging.DEBUG if DEBUG else logging.INFO
logging.basicConfig(stream=sys.stderr, level=log_level)

def init_perl():
    global perl_proc, ws
    logging.debug("Starting perl script...")
    perl_proc = subprocess.Popen(["perl", perl_script])
    while True:
        try:
            ws = create_connection("ws://{}:{}/websocket"\
                                    .format(DISAMB_ADDR, DISAMB_PORT))
            break
        except:
            continue
    logging.debug("Connection to perl script is established")

"""
    Check if the perl script is running: if not run it again
"""
def check_perl():
    global perl_proc, ws
    logging.debug("Checking perl...")
    poll = perl_proc.poll()
    if poll is not None:
          # re-swapn the process
          logging.debug("WARNING: Perl process is dies for some reason. Restarting.")
          init_perl()

def init_fst():
    logging.debug("Loading FST...")
    TurkishMorphology.load_lexicon('turkish.fst')

"""
Initialize everything
"""
def init():
    init_fst()
    init_perl()

"""
Returns list of lists: where each list is morphological parses of a sentence
"""
def parse_lines(text):
    logging.debug("Parsing...")
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

"""
Call perl routines for disambiguation
"""
def disambiguate(parsed_text):
    check_perl()
    ws.send(parsed_text)
    result = ws.recv()
    return result

def evaluate(text):
	parsed_text = parse_lines(inp)
	result = disambiguate(parsed_text)
	return result

def clear():
	ws.close()
