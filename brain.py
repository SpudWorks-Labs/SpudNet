"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                            Company: SpudWorks.
                        Program Name: SpudNet.
      Description: A helpful AI Assistant that act as the host device.
                             File: brain.py
                            Date: 2026/02/04
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


# ~ Import Third-Party Modules. ~ #
import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# ~ Import Local Modules. ~ #
import system_monitor
import vocal
import database


# ~ Initialize global constants. ~ #
APP = FastAPI(title="SpudNet Brain", version="1.1")


class ChatRequest(BaseModel):
    """
    ~ Pydantic validator for the user message. ~

    Attributes:
        message               (String) : The message sent from the user.
    """

    message: str


@APP.get('/status')
async def get_system_status():
    """
    ~ Get the status and log it for trend analysis. ~

    Returns:
        String                         : The status of the device.
    """

    stats = system_monitor.get_system_info()
    database.log_system_stats(stats)

    return stats


@APP.post('/chat')
async def chat_stream(request: ChatRequest):
    """
    ~ Streams responses and saves conversations to DB upon completion. ~

    Arguments:
        request          (ChatRequest) : An object containing the 
                                         message from the user.

    Functions:
        saving_generator               : Takes the message and and saves the 
                                         message and its reply in the database.

    Returns:
        StreamingResponse              : The streamed response from the LLM.
    """

    async def saving_generator(msg):
        """
        ~ The function to save the conversation in the database. ~

        Arguments:
            msg                        : The message from the user.
        """
        
        full_response = ""

        async for chunk in vocal.async_talk(msg):
            full_response += chunk
            yield chunk

        database.log_chat(msg, full_response)

    return StreamingResponse(saving_generator(request.message), media_type="text/plain")


@APP.get('/history')
async def get_history():
    """
    ~ Retrieve the last 10 snapshots and conversations. ~

    Returns:
        Dict                           : The history of the information saved.
    """

    return {
        "hardware_history": database.get_recent_metrics(limit=10),
        "chat_history": database.get_recent_chats(limit=10)
    }


if __name__ == "__main__":
    # ~ Check if Ollama is running. ~ #
    # Maybe add a background daemon or something to ensure
    # the vocal model is able to speak. Could also implement this
    # in the vocal module itself since that is what requires it.

    # ~ Run the brains API Server at 127.0.0.1:42069 and catch errors. ~ #
    print(">>> SpudNet Brain Online at http://127.0.0.1:42069")
    try:
        uvicorn.run(APP, host="127.0.0.1", port=42069, log_level="info")
    except Exception as e:
        print(f"There has been an error: {e}")
