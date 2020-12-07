#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Hasim Sak
#Description: An example python script to use the stochastic morphological parser for Turkish.

import sys
import re
import morphological_parser_sak.TurkishMorphology as TurkishMorphology
import subprocess
import flask
import logging
import os
import atexit
import asyncio
import time
from websocket import create_connection

try:
    import importlib.resources as pkg_resources
except ImportError:
    import importlib_resources as pkg_resources

"""
This is supposed to run in a container. The port selection is arbitrary
    since there is not much of a process running
"""
DISAMB_ADDR = "127.0.0.1"
DISAMB_PORT = 34215
perl_script = "md.pl"
uri = "ws://{}:{}/websocket".format(DISAMB_ADDR, DISAMB_PORT)
perl_proc = None
DEBUG = False 
ws = None

with pkg_resources.path(__package__, "turkish.fst") as p:
    fst_path = str(p.resolve())
    base_path = str(p.resolve().parent)

log_level = logging.DEBUG if DEBUG else logging.INFO
logging.basicConfig(stream=sys.stderr, level=log_level)

def init_perl():
    global perl_proc, ws
    logging.debug("Starting perl script...")
    # run in base_path dir
    perl_proc = subprocess.Popen(["perl", perl_script], cwd=base_path)
    while True:
        try:
            ws = create_connection(uri)
            break
        except Exception as e:
            time.sleep(0.1)
            logging.debug(e)
            logging.debug("Retrying...")
            continue
    logging.debug("Connection to perl script is established")

"""
    Check if the perl script is running: if not run it again
"""
def check_perl():
    global perl_proc
    logging.debug("Checking perl...")
    poll = perl_proc.poll()
    if poll is not None:
          # re-swapn the process
          logging.debug("WARNING: Perl process is died for some reason. Restarting.")
          init_perl()

def init_fst():
    logging.debug("Loading FST...")
    TurkishMorphology.load_lexicon(fst_path)

"""
Initialize everything
"""
def init():
    init_fst()
    init_perl()

def cleanup():
    if perl_proc:
        perl_proc.terminate()
    if ws:
        ws.close()

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

"""
Call perl routines for disambiguation
"""
def disambiguate(parsed_text):
    try:
        ws.send(parsed_text)
        result = ws.recv()
    except:
        # the process might have died
        check_perl()
        time.sleep(0.5)
        return disambiguate(parsed_text)
    return result

def evaluate(text):
    result = ""
    threshold = 2**10
    msg_arr = []
    msg_size = 0
    lines = [x for x in text.strip().split("\n") if x]
    for i, line in enumerate(lines):
        msg_size += len(line)
        if msg_size >= threshold:
            parsed_text = parse_lines(msg_arr)
            result += disambiguate(parsed_text)
            msg_size = len(line)
            msg_arr = []
        msg_arr.append(line)

    if msg_arr:
        parsed_text = parse_lines(msg_arr)
        result += disambiguate(parsed_text)
    
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
