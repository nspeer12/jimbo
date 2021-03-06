import markdown
from flask import Flask, render_template, request, jsonify, make_response
import markdown.extensions.fenced_code
from pygments.formatters import HtmlFormatter
import random
import json
import requests
import re
import time


app = Flask(__name__)
app.static_folder = "static"

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/privacy-policy")
def privacy():
    return render_template("privacy-policy.html")


@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    # parse data from request
    if request.method == "POST":
        #determine if voice or text output


        req = request.get_json(silent=True, force=True)

        f = open("logs/" + str(time.time()) + ".txt", "w")
        f.write(json.dumps(req, indent=4, sort_keys=True))
        f.close()
        
        # get intent 
        intent = req["queryResult"]["intent"]["displayName"]
        print(intent)
        params = req["queryResult"]["parameters"]

        if "define" in intent:
            if "phrase" in params and params["phrase"] is not None:
                phrase = params["phrase"]
                res = define(phrase)
                res = assistant_response(res)
                res = json.dumps(res, indent=4)
                r = make_response(res)
                r.headers["Content-Type"]="application/json"
                return r
        elif "joke" in intent:
            with open("jokes/nsfw.json") as f:
                data = json.load(f)
                joke = random.choice(data["jokes"])
                res = assistant_response(joke)
                res = json.dumps(res, indent=4)
                r = make_response(res)
                r.headers["Content-Type"] = "application/json"
                return r


def define(phrase):
    url = "https://mashape-community-urban-dictionary.p.rapidapi.com/define"

    querystring = {"term": phrase}

    headers = {
        "x-rapidapi-host": "mashape-community-urban-dictionary.p.rapidapi.com",
        "x-rapidapi-key": "a9520b2012mshe2a098d392901cfp18b21ejsn7cd5055df26e"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    definition = json.loads(response.text)

    # parse definition from json
    if len(definition["list"]) > 0:
        if "definition" in definition["list"][0]:
            definition = definition["list"][0]["definition"]
            definition = definition.replace("[", "")
            definition = definition.replace("]", "")
           
            print(definition)
            return definition
    else:
        return "Oh shit, something went wrong. Try again in a few minutes"


def fulfillment_message(text):
    return {
        "fulfillmentMessages": [
            {
                "text": {
                    "text": [
                        text
                    ]
                }
            }
        ]
    }


def assistant_response(text, response=False):
    return {
            "payload": {
                "google": {
                    "expectUserResponse": response,
                    "richResponse": {
                        "items": [
                            {
                                "simpleResponse": {
                                    "textToSpeech": text
                                }
                            }
                        ]
                    }
                }
            }
        }



if  __name__ == "__main__":
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.run(port=5000)
