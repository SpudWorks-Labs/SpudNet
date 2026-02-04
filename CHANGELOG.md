*Note:* All time is in ***UTC***.


*2026/01/28*
* 18:36
    - Created the base of the project.
    - The TUI looks good and the chatting works.
    - Need some minor UI fixes and a lot of improvements.
    
* 22:09
    - Fixed some UI issues and introduced text-wrapping and scroll limits.

*2026/01/29*
* 04:50
    - Starting to rewrite the main file for cleaner code.

*2026/02/02*
* 16:51
    - Beginning to start the skeleton for "Phase 1".

* 16:56
    - The virtual environment has been initialized, and the
      `requirements.txt` has been created.

* 17:08
    - Filestamps were updated.

* 17:20
    - The `ARCHITECTURE.md` file was created and added to.

* 17:55
    - In a review of the `system_monitor.py` there has been a discovery of a
      `df` parsing problem. A long name could make it return the wrong line.
    - The skeleton is now finished, now it's time to test it.

* 19:29
    - Updated the `Modelfile` and created a script to create the model.
    - The `create_model.sh` file can be made much more robust.

*2026/02/03*
* 04:22
    - Integrated the `get_system_info()` dict into the LLMs prompt.
    - Made the `create_model.sh` more robust and handle errors better.

* 04:32
    - Fixed the `df` parsing problem by using `psutil.disk_partitions(all=False)`
      and checking for 
      
*2026/02/04*
* 03:29
    - Fixed multi-lined messages so they stack properly.
    - Continuing to test to see if the other two issues have been fixed.

* 03:32
    - Responses take a very long time. There might 
      be a latency issue within the pipeline.
    
* 03:35
    - The text does not leave the text field, but the text is not able to be
      scrolled through

* 03:46
    - The scrolling issue was caused by the AI suggesting to use 
      the `PAGEUP` and `PAGEDOWN` attributes in `self.term` but the correct
      attributes are: `PGUP` and `PGDOWN`.

* 05:09
    - Fixed and updated latency issues with `asyncio`, now still constrained by
      the power of a CPU.

* 05:37
    - Added the `database.py` and `server.py` for Phase 2.
    
* 07:30
    - Things are "functional" but the issue is how the response is returned.
    - The response is a large, recursive garbled string.

### TO-DO
[!!!!!] Make the response actually legible and not recursive.
    * Possible Fix:
        Update `main._get_llm_response()`:
            - This method only sends he new piece of text instead of the cumulative history.
            ```python
            async def _get_llm_response(self, user_msg):
            try:
                # ... (keep snapshot logic) ...
                response = requests.post(f"{self.api_url}/chat", json={"message": full_msg_with_snapshot}, stream=True)
                response.raise_for_status()

                # Send chunks individually as they arrive
                for chunk in response.iter_content(chunk_size=None):
                    if chunk:
                        await self.llm_response_queue.put(chunk.decode("utf-8"))

            except Exception as e:
                await self.llm_response_queue.put(f"[SpudNet error] {e}")
            ```

        Update `main.execute()`:
            - Queue processing logic needs to update the last message if it
              belongs to SpudNet, rather than creating a new one.
            ```python
            # Inside the 'while not self.llm_response_queue.empty():' block
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
            ```
[!!!] Switch from `requests` to `httpx.AyncClient` in `main.py`. 

