# SpudNet

SpudNet is a system-integrated agentic daemon with a TUI menu that provides hardware-aware automation, real-time system monitoring, and cross-network project assistance on its host devices.


### Architecture

SpudNet operates as a persistent background daemon (Phase 2) that interfaces with the Linux kernel via Python, with plans to allow for more devices in the future. The system prioritizes safety through Btrfs snapshots before executing root-level changes, and with human review.

* *Vocal Model:* Powered by the `SpudNet-Vocal` model via Ollama for concise, peer-level technical advice.
* *Interface:* A high-performance TUI built with `blessed`, featuring real-time command processing.
* *Hardware Layer:* Utilizes `psutil` and `subprocess` for deep system state awareness. (Phase 1)


### Development Roadmap

* **Phase 1 (The Nervous System):** Focus on psutil integration and JSON snapshots.
* **Phase 2 (The Cognitive Pipeline):** Transition to the FastAPI daemon and SQLite.
* **Phase 3 (The Workspace Layer):** Implement watchdog for project indexing.
* **Phase 4 (The Guardian):** Focus on security, sudo logic, and Btrfs snapshots.
* **Phase 5 (The Mesh Network):** Networking and P2P synchronization.

### Installation & Quick-Start
First, clone the repo and enter the project:
```bash
git clone https://github.com/SpudWorks-Labs/SpudNet
cd SpudNet
```

Second, create a virtual environment and install the requirements.
```bash
python -m venv env
source ./env/bin/activate
pip install -r requirements.txt
```

Finally, start the TUI client.
```bash
python main.py
```

* */clear*: Wipes the terminal buffer.
* */kill*: Safely terminate the session.

### Important Acknowledgements
This project was made by human developers, with the use of AI Tooling.
