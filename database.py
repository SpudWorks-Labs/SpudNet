"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                            Company: SpudWorks.
                        Program Name: Live Translate.
      Description: A helpful AI Assistent that act as the host device.
                            File: database.py
                            Date: 2026/02/04
                        Version: 0.1-2026.02.04

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

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""


import sqlite3
import json
from datetime import datetime


DB_FILE = "spudnet.db"

def get_connection():
    """
    ~ Establshes a connection to the SQLite database. ~
    """

    return sqlite3.connect(DB_FILE)


def init_db():
    """
    ~ Initializes the database tables if they do not exist. ~
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hardware_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            data JSON NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            user_msg TEXT,
            spudnet_msg TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print(f"Database {DB_FILE} initialized!")


def log_system_stats(stats_dict):
    """
    ~ Saves the get_system_info() dictionary as a JSON string. ~
    """

    conn = get_connection()
    timestamp = stats_dict.get("timestamp", datetime,now().isoformat())

    with conn:
        conn.execute(
            "INSERT INTO hardware_metrics (timestamp, data) VALUES (?, ?)",
            (timestamp, json.dumps(stats_dict))
        )

    conn.close()


def log_chat(user_msg, spudnet_msg):
    """
    ~ Logs a conversation pair. ~
    """

    conn = get_connection()
    timestamp = datetime.now().isoformat()

    with conn:
        conn.execute(
            "INSERT INTO conversations (timestamp, user_msg, spudnet_msg) VALUES (?, ?, ?)",
            (timestamp, user_msg, spudnet_msg)
        )


def get_recent_metrics(limit=10):
    """
    ~ Retrieves the last N hardware snapshots. ~
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT data FROM hardware_metrics ORDER BY od BY DESC LIMIT ?",
        (limit,)
    )

    rows = cursor.fetchall()
    conn.close()

    return [json.loads(row[0]) for row in rows]


if __name__ == "__main__":
    init_db()
