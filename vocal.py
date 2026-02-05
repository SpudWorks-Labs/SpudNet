"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                            Company: SpudWorks.
                        Program Name: SpudNet.
      Description: A helpful AI Assistant that act as the host device.
                             File: vocal.py
                            Date: 2026/01/28
                        Version: 1.8.1-2026.02.05

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

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""


# ~ Import Standard Modules. ~ #
import asyncio
import json

# ~ Import Third-Party Modules. ~ #
import httpx


# ~ Create the global constant variables. ~ #
MODEL = "SpudNet-Vocal:latest"
OLLAMA_API_BASE_URL = "http://localhost:11434/api/generate"


async def async_talk(msg):
    """
    ~ Asynchronously send message to the LLM model. ~
    
    Returns: 
        - String                       : The response or an error.
    """

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                OLLAMA_API_BASE_URL,
                json={
                    "model": MODEL,
                    "prompt": msg,
                    "stream": True
                },
                timeout=None
            )
            response.raise_for_status()

            json_buffer = ""
            async for chunk_bytes in response.aiter_bytes():
                chunk_str = chunk_bytes.decode('utf-8')
                json_buffer += chunk_str

                while '\n' in json_buffer:
                    line, json_buffer = json_buffer.split('\n', 1)
                    
                    if line.strip():
                        try:
                            chunk_data = json.loads(line)
                            if "response" in chunk_data:
                                yield chunk_data["response"]

                        except json.JSONDecodeError:
                            pass
    
    except httpx.RequestError as e:
        yield f"[SpudNet Error] HTTP Request failed: {e}"

    except httpx.HTTPStatusError as e:
        error = e.response.text
        error_code = e.response.status_code
        yield f"[SpudNet Error] HTTP Status Error: {error_code} - {error}"

    except Exception as e:
        yield f"[SpudNet Error] Received the foolowin error: {e}"
