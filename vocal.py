"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""


import asyncio
import httpx
import json

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
                timeout=None  # Disable timeout for long-running LLM calls
            )
            response.raise_for_status()

            full_response = ""
            async for chunk_bytes in response.aiter_bytes():
                chunk_str = chunk_bytes.decode('utf-8')
                for line in chunk_str.splitlines():
                    if line.strip():
                        try:
                            chunk_data = json.loads(line)
                            full_response += chunk_data.get("response", "")
                        except json.JSONDecodeError:
                            # Handle cases where a line might not be a complete JSON object
                            pass
            return full_response
    
    except httpx.RequestError as e:
        return f"[SpudNet error] HTTP Request failed: {e}"
    except httpx.HTTPStatusError as e:
        return f"[SpudNet error] HTTP Status Error: {e.response.status_code} - {e.response.text}" 
    except Exception as e:
        return f"[SpudNet error] Could not reach Ollama or process response: {e}"
