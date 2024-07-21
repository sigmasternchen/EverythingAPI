from __future__ import annotations

import json
import os

from dotenv import load_dotenv
from flask import Flask, request, Response
from openai import OpenAI
from groq import Groq

SYSTEM_PROMPT = """
    You are the "Everything API" that can deal with all sorts of data and operations.
    Answer all requests with some valid JSON that fits the given request.
    Make sure to only return valid JSON. The response should not contain any comments or ellipsis.

    For example: Assume you get a request for /cars/123 with method GET, your response could look like this:
    {
        "id": 123,
        "make": "Toyota",
        "model": "Camry",
        "year": 2021,
        "color": "Silver",
        "mileage": 15000,
        "engine": {
            "type": "V6",
            "horsepower": 301
        },
        "transmission": "Automatic",
        "features": ["Leather seats", "Sunroof", "Navigation system"],
        "price": 25000
    }
    """
USER_PROMPT = """
    URI: {uri}
    Method: {method}
    Request Body:
    {body}
    """

ai: OpenAI | Groq | None = None

app = Flask(__name__)


@app.route("/")
def root():
    return Response(
        '{"motd": "Welcome to the Everything API. Please provide an endpoint."}',
        mimetype='application/json'
    )


@app.route("/favicon.ico")
def favicon():
    return Response('{"error": "not found"}', status=404, mimetype='application/json')


@app.route("/<path:path>")
def handler(path):
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": USER_PROMPT.format(
                uri=request.url,
                method=request.method,
                body=request.data[:500]
            )
        }
    ]

    print("request:", request.method, request.url, request.data)

    for i in range(0, 5):
        try:
            response = ai.chat.completions.create(
                # model="gpt-3.5-turbo",
                model="llama3-70b-8192",
                messages=messages
            ).choices[0].message.content
            json.loads(response)  # verify response

            print("response: " + response)
            return Response(response, status=200, mimetype="application/json")
        except ValueError:
            print("response not parseable: " + response)
            continue

    return Response('{"error": "internal error"}', status=500, mimetype='application/json')


def main():
    global ai
    load_dotenv()
    # ai = OpenAI(api_key=os.environ["OPENAI_TOKEN"])
    ai = Groq(api_key=os.environ["GROQ_TOKEN"])
    app.run()


if __name__ == "__main__":
    main()
