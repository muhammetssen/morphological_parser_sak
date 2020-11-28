from flask import Flask, json, g, request
import mp
import atexit


mp.init()
app = Flask(__name__)

def clear():
    mp.clear()
atexit.register(clear)

@app.route("/evaluate", methods=["POST"])
def evaluate():
    json_data = json.loads(request.data)
    input_text = json_data["query"]
    result = mp.evaluate(input_text)
    return json_response({"result": result}, 200)
