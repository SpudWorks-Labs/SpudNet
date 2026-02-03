# Architecture

SpudNet operates as a persistent background daemon (Phase 2) that interfaces with the Linux kernel via Python, with plans to allow for more devices in the future. The system prioritizes safety through Btrfs snapshots before executing root-level changes, and with human review.

* *Vocal Model:* Powered by the `SpudNet-Vocal` model via Ollama for concise, peer-level technical advice.
* *Interface:* A high-performance TUI built with `blessed`, featuring real-time command processing.
* *Hardware Layer:* Utilizes `psutil` and `subprocess` for deep system state awareness. (Phase 1)


Phase 1; The Nervous System:
    **Status:** Complete.

    **New Dependencies:**
        * `psutil`

    - This phase revolves around creating a "Data Contract" for the LLM to parse.
    - The following is a JSON structure with the required information:
        ```json
            {
                "timestamp": iso8601,
                "cpu": {
                    "usage_pct": usage_pct, "core_count": core_count, "load_avg": load_avg
                },
                "memory": {
                    "total_gb": total_gb,
                    "avail_gb": avail_gb,
                    "used_pct": used_pct
                },
                "storage": {
                    "path": path,
                    "total_gb": total_gb,
                    "free_gb": free_gb,
                    "fs_type": fs_type
                },
                "status": "online" | "warning" | "critical"
            }
        ```

    - Return that from a function.


Phase 2; The Cognitive Pipeline:
    **Status:** In-Progress.

    ***New Dependancies:***
        * `fastapi`
        * `uvicorn`
        * `requests`

    - Host `server.py` in a serparate terminal and host on localhost:8000
      with `main.py` open in another.

    - Initiate the database at startup so `/status` 
      and `/history` can be functional.

    **The Server:** `server.py`
        Import the system monitor and vocal modules.
        The `POST /chat` needs to return a 
        `Streaming Response` (`fastapi.responses`) so that the
        communication feels live.

    **The Database:** `database.py`
        * `database.py`: Contains the logic to handle
        connections, creating tables, and runs queries.
        * `spudnet.db`: The actual SQLite database.

    **The Client:** `main.py`
        Instead of calling the vocals module, use `import requests` or `httpx`.
        Iterate through the API response like the generator does in `vocal.py`.

    
