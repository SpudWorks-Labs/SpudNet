"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                            Company: SpudWorks.
                        Program Name: Live Translate.
      Description: A helpful AI Assistent that act as the host device.
                             File: server.py
                            Date: 2026/02/04
                        Version: 1.1-2026.02.04

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


import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

import system_monitor
import vocal
import database


app = FastAPI(title="SpudNet Daemon", version="1.1")


class ChatRequest(BaseModel):
    message: str


@app.get('/status')
async def get_system_status():
    """
    ~ Get the status of the system. ~

    Returns:
        Dict                           : The JSON of the system status.
    """

    return system_monitor.get_system_info()


@app.post('/chat')
async def chat_stream(request: ChatRequest):
    """
    ~ Streams the vocal model's response directly to the client.
      Using text/plain allows the client to print chunks as they arrive. ~

    Returns:
        Generator                      : The streaming chunks buffer.
    """

    return StreamingResponse(vocal.async_talk(request.message), media_type="text/plain")


@app.get('/history')
async def get_history():
    """
    ~ Placeholder for database retrieval. ~

    Returns:
        Dict                           : A placeholder for functionality.
    """

    return {"message": "Not implemented yet. Connect database.py first."}


if __name__ == "__main__":
    print(">>> SpudNet Daemon Online at http://127.0.0.1:8000")

    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
