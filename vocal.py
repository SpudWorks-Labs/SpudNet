#2026/01/28

import ollama

MODEL = "SpudNet-Vocal"

def talk(msg):
    streamed = ollama.generate(
        model=MODEL,
        prompt=msg,
        stream=True
    )
    response = ""

    for chunk in streamed:
        response += chunk["response"]
        # print(chunk['message']['content'], end='', flush=True)

    return response


# for word in talk("Hello"):
#     print(word, end='', flush=True)
