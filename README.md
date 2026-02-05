# SpudNet

SpudNet is a system-integrated agentic daemon with a TUI menu that provides hardware-aware automation, real-time system monitoring, and cross-network project assistance on its host devices.

---

### Requirements & Tech
* Python == 3.14.2
* blessed == 1.29.0
* ollama >= 0.4.0
* psutil == 3.3.14
* pydantic == 2.12.5


---

### Architecture
You can view the architecture of the project at the [ARCHITECTURE](ARCHITECTURE.md) file.

### Documentation
You can view the [CHANGELOG](CHANGELOG.md) to view more information.


### Development Roadmap

* **Phase 1 (The Nervous System) *Finished*:** Focus on psutil integration and JSON snapshots.
* **Phase 2 (The Cognitive Pipeline) *In-progress*:** Transition to the FastAPI daemon and SQLite.
* **Phase 3 (The Workspace Layer):** Implement watchdog for project indexing.
* **Phase 4 (The Guardian):** Focus on security, sudo logic, and Btrfs snapshots.
* **Phase 5 (The Mesh Network):** Networking and P2P synchronization.

---

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

Then create the model by running the `create_model.sh`.
```bash
# In a separate terminal.
ollama serve

# (Back in the original terminal) Create the model.
./create_model.sh
```

Start the brain in another terminal.
```bash
python brain.py
```

Optionally, you can daemonize the file like so:
```bash
sudo cp spudnet.service /etc/systemd/system/
sudo systemctl enable spudnet.service
sudo systemctl start spudnet.service
```
That ensures the server is always running in the background.

Finally, start the TUI client.
```bash
python main.py
```

* */clear*: Wipes the terminal buffer.
* */kill*: Safely terminate the session.


---

### Important Acknowledgements
This project was made by human developers, with the use of AI Tooling.
