"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                            Company: SpudWorks.
                        Program Name: SpudNet.
      Description: A helpful AI Assistant that act as the host device.
                            File: database.py
                            Date: 2026/02/04
                        Version: 1.8.1-2026.02.05

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


# ~ Standard Library Imports ~ #
import sqlite3
import json
from datetime import datetime


# ~ Create the database file constant. ~ #
DB_FILE = "spudnet.db"


def get_connection():
    """
    ~ Establish a connection to the SQLite database. ~

    Return:
        - sqlite3.Connection           : The database connection object.
    """

    return sqlite3.connect(DB_FILE)


def init_db():
    """
    ~ Initialize the database tables if they do not exist. ~
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
    ~ Save the get_system_info() dictionary as a JSON string to the database. ~

    Arguments:
        - stats_dict            (Dict) : The system information dictionary.
    """

    conn = get_connection()
    timestamp = stats_dict.get("timestamp", datetime.now().isoformat())

    with conn:
        conn.execute(
            "INSERT INTO hardware_metrics (timestamp, data) VALUES (?, ?)",
            (timestamp, json.dumps(stats_dict))
        )

    conn.close()


def log_chat(user_msg, spudnet_msg):
    """
    ~ Log a conversation message pair to the database. ~

    Arguments:
        - user_msg            (String) : The user's message.
        - spudnet_msg         (String) : The SpudNet response.
    """

    conn = get_connection()
    timestamp = datetime.now().isoformat()
    command = "INSERT INTO conversations \
                (timestamp, user_msg, spudnet_msg) \
                VALUES (?, ?, ?)"

    with conn:
        conn.execute(
            command,
            (timestamp, user_msg, spudnet_msg)
        )


def get_recent_metrics(limit=10):
    """
    ~ Retrieve the most recent N hardware metrics snapshots. ~

    Arguments:
        - limit                  (Int) : Maximum number of rows to return.

    Return:
        - List[Dict]                   : List of hardware metrics dictionaries.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT data FROM hardware_metrics ORDER BY id DESC LIMIT ?",
        (limit,)
    )

    rows = cursor.fetchall()
    conn.close()

    return [json.loads(row[0]) for row in rows]


def get_recent_chats(limit=20):
    """
    ~ Retrieve the most recent N conversation message pairs. ~

    Arguments:
        - limit                  (Int) : Maximum number of rows to return.

    Return:
        - List[Dict]                   : List of chat pair dictionaries.
    """

    conn = get_connection()
    cursor = conn.cursor()
    command = "SELECT timestamp, user_msg, spudnet_msg \
                FROM conversations ORDER BY id DESC LIMIT ?"
    cursor.execute(
        command,
        (limit,)
    )

    rows = cursor.fetchall()
    conn.close()

    return [{"timestamp": r[0], "user": r[1], "spudnet": r[2]} for r in rows]


if __name__ == "__main__":
    init_db()
