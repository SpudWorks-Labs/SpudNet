"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                            Company: SpudWorks.
                        Program Name: Live Translate.
      Description: A helpful AI Assistent that act as the host device.
                             File: brain.py
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


app = FastAPI(title="SpudNet Brain", version="1.1")


class ChatRequest(BaseModel):
    message: str


@app.get('/status')
async def get_system_status():
    """
    ~ Get the status and log it for trend analysis. ~
    """

    stats = system_monitor.get_system_info()
    database.log_system_stats(stats)

    return stats


@app.post('/chat')
async def chat_stream(request: ChatRequest):
    """
    ~ Streams responses and saves conversations to DB upon completion. ~
    """

    async def saving_generator(msg):
        full_response = ""

        async for chunk in vocal.async_talk(msg):
            full_response += chunk
            yield chunk

        database.log_chat(msg, full_response)

    return StreamingResponse(saving_generator(request.message), media_type="text/plain")


@app.get('/history')
async def get_history():
    """
    ~ Retrieve the last 10 snapshots and conversations. ~
    """

    return {
        "hardware_history": database.get_recent_metrics(limit=10),
        "chat_history": database.get_recent_chats(limit=10)
    }


if __name__ == "__main__":
    print(">>> SpudNet Brain Online at http://127.0.0.1:42069")

    try:
        uvicorn.run(app, host="127.0.0.1", port=42069, log_level="info")
    except Exception as e:
        print(f"There has been an error: {e}")
