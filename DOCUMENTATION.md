*Note:* All time is in ***UTC***.


*2026/01/28*
* 18:36
    - Created the base of the project.
    - The TUI looks good and the chatting works.
    - Need some minor UI fixes and a lot of improvements.
    
* 22:09
    - Fixed some UI issues and introduced text-wrapping and scroll limits.

*2026/01/09*
* 04:50
    - Starting to rewrite the main file for cleaner code.

*2026/02/02*
* 16:51
    - Beginning to start the skeleton for "Phase 1".

* 16:56
    - The virtual environment has been initialized, and the
      `requirements.txt` has been created.

* 17:08
    - Filestamps where updated.

* 17:20
    - The `ARCHITECTURE.md` file was created and added to.

* 17:55
    - In a review of the `system_monitor.py` there has been a discovery of a
      `df` parsing problem. A long name could make it return the wrong line.
    - The skeleton is now finished, now time to test it.


### TO-DO
[!] Connect the `get_system_info()` output dictionary to the vocal module.
[!] Fix the `df` parsing problem: Line 77 in `system_monitor.py` with `psutil.disk_partition(all=False)`
