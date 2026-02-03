"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                            Company: SpudWorks.
                        Program Name: Live Translate.
      Description: A helpful AI Assistent that act as the host device.
                         File: system_monitor.py
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


import psutil
import json
import subprocess
from datetime import datetime


def get_cpu_info():
    """
    ~ Get the percentage, core count and load average. ~

    Return:
        - dict                         : The CPU information.
    """

    return {
        "usage_pct": psutil.cpu_percent(interval=0.1),
        "core_count": psutil.cpu_count(),
        "load_avg": psutil.getloadavg()
    }


def get_memory_info():
    """
    ~ Get the total, available and used percentage. ~
    Return:
        - dict                         : The memory information.
    """

    return {
        "total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "avail_gb": round(psutil.virtual_memory().available / (1024**3), 2),
        "used_pct": psutil.virtual_memory().percent
    }


def get_storage_info():
    """

    ~ Get the path, total GB, free GB and filesystem type. ~

    Return:
        - dict                         : The storage information.
    """
    # Get root disk usage info
    root_disk_usage = psutil.disk_usage('/')

    fs_type = None
    path = None

    for part in psutil.disk_partitions(all=False):
        if part.mountpoint == '/':
            fs_type = part.fstype
            path = part.mountpoint

    return {
        "path": path,
        "total_gb": round(root_disk_usage.total / (1024**3), 2),
        "free_gb": round(root_disk_usage.free / (1024**3), 2),
        "fs_type": fs_type
    }


def get_status(cpu_info, memory_info, storage_info):
    """

    ~ Get the status of the system. ~

    Arguments:
        - cpu_info             (dict) : The CPU information.
        - memory_info          (dict) : The memory information.
        - storage_info         (dict) : The storage information.

    Return:
        - str                          : The status of the system.
    """

    current_status = "online"

    # ~ Check the CPU usage. ~ #
    if cpu_info["usage_pct"] > 80:
        current_status = "critical"
    elif cpu_info["usage_pct"] > 60:
        if current_status != "critical":
            current_status = "warning"

    # ~ Check the memory usage. ~ #
    if memory_info["used_pct"] > 80:
        current_status = "critical"
    elif memory_info["used_pct"] > 60:
        if current_status != "critical":
            current_status = "warning"

    # ~ Check the storage usage. ~ #
    # ~ Values are in GB ~ #
    if storage_info["free_gb"] < 10:
        current_status = "critical"
    elif storage_info["free_gb"] < 20:
        if current_status != "critical":
            current_status = "warning"

    return current_status


def get_system_info():
    """
    ~ Get the information for the system. ~

    Return:
        - dict                         : The information for the system.
    """

    # ~ Get the CPU information. ~ #
    cpu_info = get_cpu_info()

    # ~ Get the memory information. ~ #
    memory_info = get_memory_info()

    # ~ Get the storage information. ~ #
    storage_info = get_storage_info()

    # ~ Get the status of the system. ~ #
    status = get_status(cpu_info, memory_info, storage_info)

    # ~ Timestamp the information. ~ #
    return {
        "timestamp": datetime.now().isoformat(),
        "cpu": cpu_info,
        "memory": memory_info,
        "storage": storage_info,
        "status": status
    }

if __name__ == "__main__":
    print(get_storage_info())
