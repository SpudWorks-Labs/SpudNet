"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                            Company: SpudWorks.
                        Program Name: Live Translate.
      Description: A helpful AI Assistent that act as the host device.
                             File: vocal.py
                            Date: 2026/01/28
                        Version: 0.1-2026.02.02

===============================================================================

                        Copyright (C) 2026 SpudWorks Labs.

        This program is free software: you can redistribute it and/or modify
        it under the terms of the GNU Affero General Public License as published
        by the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU Affero General Public License for more details.

        You should have received a copy of the GNU Affero General Public License
        along with this program. If not, see <https://www.gnu.org/licenses/>

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""


import ollama

MODEL = "SpudNet-Vocal"

def talk(msg):
    """
    ~ Send message to the LLM model. ~
    
    Returns: 
        - String                       : The response or an error.
    """
    try:
        streamed = ollama.generate(
            model=MODEL,
            prompt=msg,
            stream=True
        )
        response = ""

        for chunk in streamed:
            response += chunk.get("response", "")
    
        return response
    
    except ollama.ResponseError as e:
        return f"[SpudNet error] Model/API: {e.error}"
    
    except Exception as e:
        return f"[SpudNet error] Could not reach Ollama or process response: {e}"

