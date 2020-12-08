#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, json, g, request, jsonify
import morphological_parser.mp as mp
import atexit


mp.init()
app = Flask(__name__)

def clear():
    mp.cleanup()
atexit.register(clear)

@app.route("/evaluate", methods=["POST"])
def evaluate():
    json_data = json.loads(request.data)
    input_text = json_data["query"]
    result = mp.evaluate(input_text)
    return jsonify(result=result)

if __name__ == "__main__":
   app.run(host='0.0.0.0')