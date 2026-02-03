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


from blessed import Terminal
from time import sleep

import vocal
from system_monitor import get_system_info


class SpudNet:
    def __init__(self):
        self.messages = []
        self.welcome = "Welcome to SpudTerminal!"
        self.term = Terminal()
        self.pos = (0, 0)

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
        x, y = self.term.width//3, 1

        for char in self.welcome:
            print(self.term.move_yx(y, x) + char)
            x += 1
            sleep(0.05)

    def render(self):
        self.pos = self.create_menu()
        self.render_title()

    def run_command(self, cmd):
        if cmd == "/clear":
            self.render()
            return

        elif cmd == "/kill":
            exit(0)

    def break_message(self, speaker, full_msg):
        msg = ""
        lines = []

        for word in full_msg.split():
            if len(msg) + len(word) < self.term.width - (3 + len(speaker)):
                msg += word + " "
            else:
                lines.append(msg)
                msg = word + " "

        lines.append(msg)

        return lines

    def render_messages(self):
        max_display = (self.term.height - (self.term.height // 3)) - 4
        visible_messages = self.messages[-max_display:]

        for msg_idx, msg in enumerate(visible_messages):
            speaker = msg["speaker"]
            msg = msg["msg"]

            if speaker == "User: ":
                color = (255, 0, 0)
            else:
                color = (255, 20, 147)

            for line_idx, line in enumerate(msg):
                if line_idx == 0:
                    print(self.term.move_yx((3 + msg_idx) + line_idx, 1) + self.term.normal + speaker + self.term.color_rgb(*color) + line)

                else:
                    print(self.term.move_yx((3 + msg_idx) + line_idx, 1) + self.term.color_rgb(*color) + line)

    def add_message(self, full_msg):
        if full_msg.startswith("/"):
            self.run_command(full_msg)
            return

        self.messages.append({"speaker": "User: ", "msg": self.break_message("User: ", full_msg)})
        self.render_messages()
        full_msg = f"[SYSTEM_SNAPSHOT]: {get_system_info()}\n{full_msg}"
        self.messages.append({"speaker": "SpudNet: ", "msg": self.break_message("SpudNet: ", vocal.talk(full_msg))})
        self.render_messages()

    def execute(self):
        with self.term.fullscreen(), self.term.cbreak():
            input_buffer = ""
            lastwidth, last_height = self.term.width, self.term.height
            
            self.render()

            while True:
                input_display_length = self.term.width - 10

                if (self.term.width, self.term.height) != (lastwidth, last_height):
                    lastwidth, last_height = self.term.width, self.term.height

                    self.render()
                
                key = self.term.inkey(timeout=0.1)

                if key.code == self.term.KEY_ESCAPE:
                    break
                if key.code == self.term.KEY_ENTER:
                    loc_y, loc_x = self.term.get_location()
                    chars = loc_x - self.pos[0]
                    
                    self.add_message(input_buffer)

                    print(self.term.move_xy(self.pos[0], self.pos[1]), end="", flush=True)
                    print(" " * chars)

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
                cursor_x = self.pos[0] + len(scrolled_input)

                print(self.term.move_yx(self.pos[1], self.pos[0]) + self.term.color_rgb(255, 0, 0) + scrolled_input + self.term.normal + " ", end="")
                print(self.term.move_yx(self.pos[1], cursor_x), end="", flush=True)
    

if __name__ == '__main__':
    spudnet = SpudNet()

    spudnet.execute()
