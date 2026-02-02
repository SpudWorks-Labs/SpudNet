# Architecture

SpudNet operates as a persistent background daemon (Phase 2) that interfaces with the Linux kernel via Python, with plans to allow for more devices in the future. The system prioritizes safety through Btrfs snapshots before executing root-level changes, and with human review.

* *Vocal Model:* Powered by the `SpudNet-Vocal` model via Ollama for concise, peer-level technical advice.
* *Interface:* A high-performance TUI built with `blessed`, featuring real-time command processing.
* *Hardware Layer:* Utilizes `psutil` and `subprocess` for deep system state awareness. (Phase 1)


Phase 1:
    This phase revolves around creataing a "Data Contract" for the LLM to parse.
    The following is a JSON structure with the required information:
    ```json
        {
            timestamp: ISO-8601 string
            cpu: {usage_pct core_count load_avg}
            memory: {total_gb avail_gb used_pct} 
            storage: {path total_gb free_gb fs_type}
            status: online | warning | critical
        }
    ```
    Return that from a function.
