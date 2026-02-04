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
    - Added the `databse.py` and `server.py` for Phase 2.
    

### TO-DO
