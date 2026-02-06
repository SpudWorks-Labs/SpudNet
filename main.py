"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                            Company: SpudWorks.
                        Program Name: SpudNet.
      Description: A helpful AI Assistant that act as the host device.
                              File: main.py
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

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""


# ~ Import Standard Modules. ~ #
import asyncio
import json
import os
import sys
from time import sleep
import textwrap

# ~ Import Third-Party Modules. ~ #
from blessed import Terminal
import httpx


class SpudNet:
    """
    ~ Main interface and orchestrator for the SpudNet Assistant: 
      manages application state, user interaction, terminal UI rendering, 
      and LLM communication. ~

    Functions:
        - __init__            : Initialize interface, application state,
                                and API client.
        - get_system_info     : Asynchronously retrieve current system
                                status from API.
        - create_menu         : Draw menu UI in the terminal and return
                                cursor position.
        - render_title        : Display application title at the top of
                                the terminal.
        - render              : Render the UI and update positions.
        - run_command         : Run system or SpudNet-specific commands.
        - _msg_zone_bottom    : Get row index just below the message area
                                separator.
        - _visible_line_count : Calculate visible message rows for 
                                display area.
        - break_message       : Split a message into wrapped lines for 
                                display width.
        - _display_len        : Get display length of a given text.
        - _all_message_lines  : Return all messages as 
                                (speaker, color, line) tuples.
        - render_messages     : Render all current messages to terminal
                                display.
        - _scroll_to_bottom   : Keep scroll offset at bottom after new
                                messages.
        - add_message         : Add user message to chat log and trigger 
                                LLM response.
        - _get_llm_response   : Get LLM response for a user message
                                asynchronously.
        - execute             : Run the main program event loop and handle
                                UI updates.
    """

    def __init__(self):
        """
        ~ Initializes SpudNet main interface: sets up app state,
          terminal UI, message log, async client, and core attributes. ~

        Attributes:
            - messages          (List) : Stores chat messages between user
                                           and SpudNet.
            - welcome            (Str) : Welcome message/title for the
                                           application.
            - term  (blessed.Terminal) : Terminal UI handler for display/
                                           output.
            - pos              (Tuple) : Cursor/origin pos for rendering/UI.
            - scroll_offset      (Int) : Message lines scrolled up for
                                           history view.
            - _last_rendered_lines
                                (List) : Tracks last lines printed for
                                           redraw optimization.
            - _last_system_snapshot
                                (Dict) : Caches last fetched system info/
                                           status.
            - _last_snapshot_time
                               (Float) : Time of last system snapshot
                                           retrieval.
            - api_url            (Str) : Base URL for internal API server.
            - llm_response_queue
                       (asyncio.Queue) : Queue for LLM streaming responses.
            - client 
                   (httpx.AsyncClient) : Async HTTP client for backend/API.
        """

        self.messages = []
        self.welcome = "Welcome to SpudTerminal!"
        self.term = Terminal()
        self.pos = (0, 0)
        self.scroll_offset = 0 
        self._last_rendered_lines = []
        self._last_system_snapshot = None
        self._last_snapshot_time = 0
        self.api_url = "http://127.0.0.1:42069"
        self.llm_response_queue = asyncio.Queue()
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(300.0, read=None, connect=60.0)
        )

    async def get_system_info(self):
        """
        ~ Get latest system status from API asynchronously. ~

        Returns:
            - Dict                     : API system status or error dict.
        """

        try:
            response = await self.client.get(f"{self.api_url}/status")
            response.raise_for_status()
                
            return response.json()
        except httpx.RequestError as re:
            return {"error": f"A RequestError has occured: {re}"}
        except httpx.HTTPStatusError as se:
            return {"error": f"A Status Error has occured: {se}"}
        except Exception as e:
            return {"error": f"A general exception has occured: {e}"}

    def create_menu(self):
        """
        ~ Draws the main menu UI and returns cursor position. ~

        Returns:
            - Tuple                    : (X, Y) coordinates for text cursor
                                         in menu.
        """

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
        """
        ~ Renders the title at the top of the terminal window. ~
        """

        x = (self.term.width // 2) - (len(self.welcome) // 2)
        y = 1
        print(self.term.move_yx(y, x) + self.welcome)

    def render(self):
        """
        ~ Renders the UI and updates positions. ~
        """

        self.pos = self.create_menu()
        self.render_title()

    def run_command(self, cmd):
        """
        ~ Runs system or SpudNet-specific commands. ~

        Arguments:
            - cmd             (String) : The command to run.
        """
        
        if cmd == "/clear":
            self.render()
            return

        elif cmd == "/kill":
            exit(0)

        elif cmd == "/reload":
            os.execv(sys.executable, ['python'] + sys.argv)

    def _msg_zone_bottom(self):
        """
        ~ Gets row index just below message area separator. ~

        Returns:
            - Integer                  : Row index for input prompt start.
        """
        
        return self.term.height - (self.term.height // 3)

    def _visible_line_count(self):
        """
        ~ Calculates visible message rows for the message display area. ~

        Returns:
            - Integer                  : Number of rows available for messages.
        """
        
        return max(0, self._msg_zone_bottom() - 3)

    def break_message(self, speaker, full_msg):
        """
        ~ Splits a message into wrapped lines for display width. ~

        Arguments:
            - speaker         (String) : The message prefix speaker label.
            - full_msg        (String) : The message content.

        Returns:
            - List                     : Wrapped lines as a list of strings.
        """

        max_line_len = self.term.width - (3 + len(speaker))
        lines = textwrap.wrap(
            full_msg, max_line_len, 
            break_long_words=False, replace_whitespace=True
        )

        return lines

    def _display_len(self, text):
        """
        ~ Gets display length of text. ~

        Arguments:
            - text            (String) : The text to measure.

        Returns:
            - Integer                  : The display width of the text.
        """
        
        return len(text)

    def _all_message_lines(self):
        """
        ~ Returns all messages as (speaker, color, line) tuples. ~

        Returns:
            - List                     : (speaker, color tuple, message line)
        """
        
        lines = []
        
        for msg in self.messages:
            speaker = msg["speaker"]
            color = (255, 0, 0) if speaker == "User: " else (255, 20, 147)

            for line in msg["msg"]:
                lines.append((speaker, color, line))

        return lines

    def render_messages(self):
        """
        ~ Renders all current messages to the terminal display. ~
        """
        
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
                prefix = self.term.normal + speaker 
                prefix += self.term.color_rgb(*color)
                max_line_len = self.term.width - 2 - len(speaker)
            else:
                prefix = self.term.color_rgb(*color)
                max_line_len = self.term.width - 2
                
            if len(line) > max_line_len:
                line = line[:max_line_len]
            print(self.term.move_yx(row, 1) + prefix + line)

    def _scroll_to_bottom(self):
        """
        ~ Keep scroll offset at bottom after new messages. ~
        """
        
        total = len(self._all_message_lines())
        visible = self._visible_line_count()
        self.scroll_offset = max(0, total - visible)

    def add_message(self, full_msg):
        """
        ~ Add a user message to the chat log and trigger LLM response. ~

        Arguments:
            - full_msg        (String) : The message text input by the user.
        """

        if full_msg.startswith("/"):
            self.run_command(full_msg)
            # Future will return response and use for reply.
            return

        self.messages.append({
            "speaker": "User: ", 
            "msg": self.break_message("User: ", full_msg)
        })
        self._scroll_to_bottom()
        self.render_messages()

        asyncio.create_task(self._get_llm_response(full_msg))

    async def _get_llm_response(self, user_msg):
        """
        ~ Get the LLM response for a user message. ~
        
        Arguments:
            - user_msg        (String) : The message from the user to 
                                         send to LLM.
        """

        try:
            # Cache system info, update every 5 seconds
            current_time = asyncio.get_event_loop().time()
            delta_time = (current_time - self._last_snapshot_time)
            if self._last_system_snapshot is None or delta_time > 5:
                self._last_system_snapshot = await self.get_system_info()
                self._last_snapshot_time = current_time

            # Try to fetch chat history, but continue with empty history if it fails
            # (History is currently not used in the prompt, so failures are non-critical)
            hist = []
            async with httpx.AsyncClient(timeout=10.0) as hist_client:
                try:
                    # Use a short timeout for history fetch since it's non-critical
                    response = await hist_client.get(f"{self.api_url}/history")
                    response.raise_for_status()
                    raw = response.json().get("chat_history") or []
                #     # Database returns newest-first; reverse for chronological context.
                    hist = list(reversed(raw))
                except Exception:
                #     # Silently fail - history is optional and not currently used
                    hist = []

            # Format as readable "User: ... SpudNet: ..." so the model can use context.
            history_lines = []
            for entry in hist:
                u = entry.get("user") or ""
                s = entry.get("spudnet") or ""
                if u:
                    history_lines.append(f"User: {u}")
                if s:
                    history_lines.append(f"SpudNet: {s}")

            if history_lines:
                history = "[CHAT HISTORY]:\n" + "\n".join(history_lines)
            else:
                history = "[CHAT HISTORY]: (none yet)"

            snap = json.dumps(self._last_system_snapshot)
            snap_msg = f"[SYSTEM_SNAPSHOT]: {snap}"
            user_msg = f"[USER]: {user_msg}"
            full_msg_with_snapshot = f"{history}\n{snap_msg}\n{user_msg}"

            async with self.client.stream(
                "POST",
                f"{self.api_url}/chat", json={
                    "message": full_msg_with_snapshot
                }) as response:

                if response.status_code != 200:
                    err_code = response.status_code
                    error = f"[SpudNet Error] Server returned {err_code}"
                    await self.llm_response_queue.put(error)
                    return

                try:
                    async for chunk in response.aiter_bytes():
                        if chunk:
                            decoded_chunk = chunk.decode("utf-8")
                            await self.llm_response_queue.put(decoded_chunk)
                except httpx.ReadError as read_err:
                    # Stream was closed unexpectedly - likely server-side error
                    error_msg = (
                        "[SpudNet Error] Stream closed unexpectedly. "
                        "Possible causes: Ollama not running (start with 'ollama serve'), "
                        "model 'SpudNet-Vocal:latest' missing, or LLM generation error. "
                        "Check brain.py server logs."
                    )
                    await self.llm_response_queue.put(error_msg)
                    return

        except httpx.ReadError as read_err:
            # Stream read error - connection closed unexpectedly
            error_msg = (
                "[SpudNet Error] Stream read failed - connection closed unexpectedly. "
                "Possible causes: Ollama not running (start with 'ollama serve'), "
                "model 'SpudNet-Vocal:latest' missing, or LLM generation error. "
                "Check brain.py server logs for details."
            )
            await self.llm_response_queue.put(error_msg)
            
        except httpx.RequestError as re:
            # Extract more details from the request error
            error_type = type(re).__name__
            error_details = []
            
            # Check for specific error types
            if isinstance(re, httpx.ConnectError):
                error_details.append("Cannot connect to API server")
                error_details.append(f"URL: {self.api_url}")
                error_details.append("Make sure 'python brain.py' is running")
            elif isinstance(re, httpx.TimeoutException):
                error_details.append("Request timed out")
            else:
                error_details.append(f"Request error ({error_type})")
            
            # Add URL if available
            if hasattr(re, 'request') and re.request:
                error_details.append(f"URL: {re.request.url}")
            
            # Add error message if available
            error_str = str(re).strip()
            if error_str:
                error_details.append(error_str)
            
            # Add underlying cause if available
            if hasattr(re, '__cause__') and re.__cause__:
                cause_str = str(re.__cause__).strip()
                if cause_str:
                    error_details.append(f"Cause: {cause_str}")
            
            error_msg = " | ".join(error_details) if error_details else "Connection failed - is the API server running?"
            re_error = f"[SpudNet Error] {error_msg}"
            await self.llm_response_queue.put(re_error)

        except httpx.HTTPStatusError as se:
            status_msg = f"HTTP {se.response.status_code}"
            if se.response.status_code == 404:
                status_msg += " - Endpoint not found"
            elif se.response.status_code == 500:
                status_msg += " - Server error"
            se_error = f"[SpudNet Error] {status_msg}: {se.request.url if hasattr(se, 'request') else 'Unknown URL'}"
            await self.llm_response_queue.put(se_error)

        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e) if str(e) else 'An unknown error occurred'
            error_display = f"[SpudNet Error] {error_type}: {error_msg}"
            await self.llm_response_queue.put(error_display)
        
    async def execute(self):
        """
        ~ Runs the main program event loop and handles UI updates. ~
        """

        with self.term.fullscreen(), self.term.cbreak():
            input_buffer = ""
            lastwidth, last_height = self.term.width, self.term.height
            input_display_length = 0
            
            self.render()

            while True:
                # Process LLM responses from the queue
                while not self.llm_response_queue.empty():
                    reply_chunk = await self.llm_response_queue.get()
                    speaker = self.messages[-1]["speaker"]

                    if self.messages and speaker == "SpudNet: ":
                        if "raw" not in self.messages[-1]:
                            msg = "".join(self.messages[-1]["msg"])
                            self.messages[-1]["raw"] = msg
                        
                        self.messages[-1]["raw"] += reply_chunk
                        raw = self.messages[-1]["raw"]
                        self.messages[-1]["msg"] = self.break_message(
                                                        "SpudNet: ", 
                                                        raw
                                                    )
                    else:
                        self.messages.append({
                            "speaker": "SpudNet: ", 
                            "msg": self.break_message(
                                        "SpudNet: ", 
                                        reply_chunk
                                    ),
                            "raw": reply_chunk
                        })

                    self._scroll_to_bottom()
                    self.render_messages()
                    
                    scrolled = input_buffer[-input_display_length:]
                    cursor_x = self.pos[0] + self._display_len(scrolled)
                    print(
                        self.term.move_yx(self.pos[1], 
                        self.pos[0]) + self.term.color_rgb(255, 0, 0) + 
                        scrolled + self.term.normal + " " * 
                        (input_display_length - self._display_len(scrolled)),
                        end=""
                    )
                    print(
                        self.term.move_yx(self.pos[1], cursor_x), 
                        end="", flush=True
                    )

                input_display_length = self.term.width - 10
                cur_size = (self.term.width, self.term.height)

                if cur_size != (lastwidth, last_height):
                    lastwidth, last_height = self.term.width, self.term.height

                    self.render()
                
                key = self.term.inkey(timeout=0.5)
                await asyncio.sleep(0)

                if key.code == self.term.KEY_ESCAPE:
                    break
                    
                if key.code == self.term.KEY_PGUP:
                    visible = self._visible_line_count()
                    self.scroll_offset = max(0, self.scroll_offset - visible)
                    self.render_messages()
                    print(
                        self.term.move_yx(self.pos[1], self.pos[0]) + 
                        self.term.color_rgb(255, 0, 0) + 
                        input_buffer[-input_display_length:] +
                        self.term.normal + " ", 
                        end=""
                    )
                    print(
                        self.term.move_yx(self.pos[1], self.pos[0] + 
                        len(input_buffer[-input_display_length:]))
                        , end="", flush=True
                    )
                    continue
                if key.code == self.term.KEY_PGDOWN:
                    visible = self._visible_line_count()
                    total = len(self._all_message_lines())
                    self.scroll_offset = min(max(0, total - visible), 
                                                self.scroll_offset + visible)
                    self.render_messages()
                    print(
                        self.term.move_yx(self.pos[1], self.pos[0]) + 
                        self.term.color_rgb(255, 0, 0) + 
                        input_buffer[-input_display_length:] + 
                        self.term.normal + " ", 
                        end=""
                    )
                    print(
                        self.term.move_yx(self.pos[1], self.pos[0] + 
                        len(input_buffer[-input_display_length:])), 
                        end="", flush=True
                    )
                    continue
                if key.code == self.term.KEY_ENTER:
                    loc_y, loc_x = self.term.get_location()
                    chars = loc_x - self.pos[0]
                    
                    self.add_message(input_buffer)

                    print(self.term.move_xy(
                            self.pos[0], self.pos[1]) + " " * chars)

                    input_buffer = ""

                    continue

                if key.code == self.term.KEY_BACKSPACE:
                    if input_buffer:
                        display_len = len(input_buffer)

                        if display_len > input_display_length:
                            display_len = input_display_length

                        input_buffer = input_buffer[:-1]
                        erase_x = self.pos[0] + (display_len - 1)

                        print(
                            self.term.move_yx(self.pos[1], erase_x)
                            + " ", end="", flush=True
                        )

                    continue

                if key and not key.is_sequence:
                    input_buffer += key

                scrolled = input_buffer[-input_display_length:]
                cursor_x = self.pos[0] + self._display_len(scrolled)

                print(
                    self.term.move_yx(self.pos[1], self.pos[0]) + 
                    self.term.color_rgb(255, 0, 0) + scrolled + 
                    self.term.normal + " ", end=""
                )
                print(
                    self.term.move_yx(self.pos[1], cursor_x),
                    end="", flush=True
                )
    

if __name__ == '__main__':
    spudnet = SpudNet()
    asyncio.run(spudnet.execute())
