"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                            Company: SpudWorks.
                        Program Name: Live Translate.
      Description: A helpful AI Assistent that act as the host device.
                              File: main.py
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


import asyncio
import json
from blessed import Terminal
from time import sleep
import httpx
import textwrap
import os
import sys


class SpudNet:
    def __init__(self):
        self.messages = []
        self.welcome = "Welcome to SpudTerminal!"
        self.term = Terminal()
        self.pos = (0, 0)
        self.scroll_offset = 0 
        self._last_rendered_lines = []
        self._last_system_snapshot = None
        self._last_snapshot_time = 0
        self.api_url = "http://127.0.0.1:8000"
        self.llm_response_queue = asyncio.Queue()

    async def get_system_info(self):
        try:
            async with httpx.AsyncClient() as client:

                response = await client.get(f"{self.api_url}/status")
                response.raise_for_status()
                return response.json()
        except httpx.RequestError as re:
            return {"error": f"A RequestError has occured: {re}"}
        except httpx.HTTPStatusError as se:
            return {"error": f"A Status Error has occured: {se}"}
        except Exception as e:
            return {"error": f"A general exception has occured: {e}"}

    def create_menu(self):
        x, y = 1, self.term.height-self.term.height//3

        print(self.term.clear)
        print("-" * self.term.width)

        for _ in range(self.term.height-3):
            print("|" + " " * (self.term.width-2) + "|")

        print("-" * self.term.width)
        print(self.term.move_yx(2, 1) + "-" * (self.term.width-2))
        print(self.term.move_yx(y, x) + "-" * (self.term.width-2))
        print(self.term.move_yx(y + 2, x) + " >>> ")

        y += 2
        x += 6

        return (x, y)

    def render_title(self):
        x = (self.term.width // 2) - (len(self.welcome) // 2)
        y = 1
        print(self.term.move_yx(y, x) + self.welcome)

    def render(self):
        self.pos = self.create_menu()
        self.render_title()

    def run_command(self, cmd):
        if cmd == "/clear":
            self.render()
            return

        elif cmd == "/kill":
            exit(0)

        elif cmd == "/reload":
            os.execv(sys.executable, ['python'] + sys.argv)

    def _msg_zone_bottom(self):
        """
        ~ First row below the message area (input separator row). ~
        """
        return self.term.height - (self.term.height // 3)

    def _visible_line_count(self):
        """
        ~ Number of rows available for messages (clipped to zone). ~
        """
        return max(0, self._msg_zone_bottom() - 3)

    def break_message(self, speaker, full_msg):
        max_line_len = self.term.width - (3 + len(speaker))
        lines = textwrap.wrap(full_msg, max_line_len, break_long_words=False, replace_whitespace=True)
        return lines

    def _display_len(self, text):
        return len(text)

    def _all_message_lines(self):
        """
        ~ Flatten messages into (speaker, color, line) for each logical line. ~
        """
        
        lines = []
        
        for msg in self.messages:
            speaker = msg["speaker"]
            color = (255, 0, 0) if speaker == "User: " else (255, 20, 147)
            for line in msg["msg"]:
                lines.append((speaker, color, line))
        return lines

    def render_messages(self):
        all_lines = self._all_message_lines()
        total_lines = len(all_lines)
        visible_count = self._visible_line_count()
        msg_bottom = self._msg_zone_bottom()

        max_scroll = max(0, total_lines - visible_count)
        self.scroll_offset = min(self.scroll_offset, max_scroll)
        self.scroll_offset = max(0, self.scroll_offset)

        for row in range(3, msg_bottom):
            print(self.term.move_yx(row, 1) + " " * (self.term.width - 2))

        start = self.scroll_offset
        end = min(start + visible_count, total_lines)

        for i in range(start, end):
            speaker, color, line = all_lines[i]
            row = 3 + (i - start)
            if row >= msg_bottom:
                break
                
            is_first_line = i == 0 or all_lines[i - 1][0] != speaker
            if is_first_line:
                prefix = self.term.normal + speaker + self.term.color_rgb(*color)
                max_line_len = self.term.width - 2 - len(speaker)
            else:
                prefix = self.term.color_rgb(*color)
                max_line_len = self.term.width - 2
                
            if len(line) > max_line_len:
                line = line[:max_line_len]
            print(self.term.move_yx(row, 1) + prefix + line)

    def _scroll_to_bottom(self):
        """
        ~ Keep scroll at bottom (e.g. after new messages). ~
        """
        
        total = len(self._all_message_lines())
        visible = self._visible_line_count()
        self.scroll_offset = max(0, total - visible)

    def add_message(self, full_msg):
        if full_msg.startswith("/"):
            self.run_command(full_msg)
            return

        self.messages.append({"speaker": "User: ", "msg": self.break_message("User: ", full_msg)})
        self._scroll_to_bottom()
        self.render_messages()

        asyncio.create_task(self._get_llm_response(full_msg))

    async def _get_llm_response(self, user_msg):
        try:
            # Cache system info, update every 5 seconds
            current_time = asyncio.get_event_loop().time()
            if self._last_system_snapshot is None or (current_time - self._last_snapshot_time) > 5:
                self._last_system_snapshot = await self.get_system_info()
                self._last_snapshot_time = current_time
            
            full_msg_with_snapshot = f"[SYSTEM_SNAPSHOT]: {json.dumps(self._last_system_snapshot)}\n{user_msg}"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/chat", json={
                        "message": full_msg_with_snapshot
                    }
                    # stream=True
                )
            
                response.raise_for_status()

                reply = ""
                async for chunk in response.aiter_bytes():
                    if chunk:
                        decoded_chunk = chunk.decode("utf-8")
                        reply += decoded_chunk # Accumulate the reply
                        await self.llm_response_queue.put(decoded_chunk) # Send individual chunks for real-time display

        except Exception as e:
            reply = f"[SpudNet Error] {e if str(e) else 'An unknown error occurred.'}"
        
        await self.llm_response_queue.put(reply)

    async def execute(self):
        with self.term.fullscreen(), self.term.cbreak():
            input_buffer = ""
            lastwidth, last_height = self.term.width, self.term.height
            
            self.render()

            while True:
                # Process LLM responses from the queue
                while not self.llm_response_queue.empty():
                    reply_chunk = await self.llm_response_queue.get()

                    # If the last message is from SpudNet, append the chunk to it
                    if self.messages and self.messages[-1]["speaker"] == "SpudNet: ":
                        # Use a 'raw' key to store the un-wrapped text for clean appending
                        if "raw" not in self.messages[-1]:
                            self.messages[-1]["raw"] = "".join(self.messages[-1]["msg"])
                        
                        self.messages[-1]["raw"] += reply_chunk
                        self.messages[-1]["msg"] = self.break_message("SpudNet: ", self.messages[-1]["raw"])
                    else:
                        # Otherwise, create the first entry for this response
                        self.messages.append({
                            "speaker": "SpudNet: ", 
                            "msg": self.break_message("SpudNet: ", reply_chunk),
                            "raw": reply_chunk
                        })

                    self._scroll_to_bottom()
                    self.render_messages()
                    # Re-render the input line and reposition the cursor after an LLM response
                    scrolled_input = input_buffer[-input_display_length:]
                    cursor_x = self.pos[0] + self._display_len(scrolled_input)
                    print(self.term.move_yx(self.pos[1], self.pos[0]) + self.term.color_rgb(255, 0, 0) + scrolled_input + self.term.normal + " " * (input_display_length - self._display_len(scrolled_input)), end="")
                    print(self.term.move_yx(self.pos[1], cursor_x), end="", flush=True)

                input_display_length = self.term.width - 10

                if (self.term.width, self.term.height) != (lastwidth, last_height):
                    lastwidth, last_height = self.term.width, self.term.height

                    self.render()
                
                key = self.term.inkey(timeout=0.5)
                await asyncio.sleep(0) # Allow other async tasks to run

                if key.code == self.term.KEY_ESCAPE:
                    break
                    
                if key.code == self.term.KEY_PGUP:
                    visible = self._visible_line_count()
                    self.scroll_offset = max(0, self.scroll_offset - visible)
                    self.render_messages()
                    print(self.term.move_yx(self.pos[1], self.pos[0]) + self.term.color_rgb(255, 0, 0) + input_buffer[-input_display_length:] + self.term.normal + " ", end="")
                    print(self.term.move_yx(self.pos[1], self.pos[0] + len(input_buffer[-input_display_length:])), end="", flush=True)
                    continue
                if key.code == self.term.KEY_PGDOWN:
                    visible = self._visible_line_count()
                    total = len(self._all_message_lines())
                    self.scroll_offset = min(max(0, total - visible), self.scroll_offset + visible)
                    self.render_messages()
                    print(self.term.move_yx(self.pos[1], self.pos[0]) + self.term.color_rgb(255, 0, 0) + input_buffer[-input_display_length:] + self.term.normal + " ", end="")
                    print(self.term.move_yx(self.pos[1], self.pos[0] + len(input_buffer[-input_display_length:])), end="", flush=True)
                    continue
                if key.code == self.term.KEY_ENTER:
                    loc_y, loc_x = self.term.get_location()
                    chars = loc_x - self.pos[0]
                    
                    self.add_message(input_buffer)

                    print(self.term.move_xy(self.pos[0], self.pos[1]) + " " * chars)

                    input_buffer = ""

                    continue

                if key.code == self.term.KEY_BACKSPACE:
                    if input_buffer:
                        display_len = len(input_buffer)

                        if display_len > input_display_length:
                            display_len = input_display_length

                        input_buffer = input_buffer[:-1]
                        erase_x = self.pos[0] + (display_len - 1)

                        print(self.term.move_yx(self.pos[1], erase_x) + " ", end="", flush=True)

                    continue

                if key and not key.is_sequence:
                    input_buffer += key

                scrolled_input = input_buffer[-input_display_length:]
                cursor_x = self.pos[0] + self._display_len(scrolled_input)

                print(self.term.move_yx(self.pos[1], self.pos[0]) + self.term.color_rgb(255, 0, 0) + scrolled_input + self.term.normal + " ", end="")
                print(self.term.move_yx(self.pos[1], cursor_x), end="", flush=True)
    

if __name__ == '__main__':
    spudnet = SpudNet()
    asyncio.run(spudnet.execute())
