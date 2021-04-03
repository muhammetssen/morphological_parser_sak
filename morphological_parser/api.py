#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, json, g, request, jsonify, json
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
    input_text = json_data["textarea"]
    parses = mp.get_parses_dict(input_text)
    parses_str = mp.pprint_str(parses)
    result = {"text": parses_str}
    response = app.response_class(
        response=json.dumps(result),
        status=200,
        mimetype='application/json'
    )
    return response

if __name__ == "__main__":
   app.run(host='0.0.0.0')


