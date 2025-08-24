# File: chat/conversation.py

import os
import sqlite3
from datetime import datetime
from typing import List, Tuple, Dict, Any, Optional
from typing import cast


DB_FILE = os.path.join(os.path.dirname(__file__), "data", "conversation_memory.db")

# Ensure the directory exists
os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)


def _connect() -> sqlite3.Connection:
    """
    Open a SQLite connection with row access by column name.
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    # Keep FK behavior consistent even if we ever add constraints that matter.
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


# Ensure the tables exist
def init_db() -> None:
    print("[DB INIT] Initializing database and creating tables...")
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER,
                sender TEXT,
                message TEXT,
                model TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(conversation_id) REFERENCES conversations(id)
            )
            """
        )
        # Helpful index when loading a conversation
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_messages_convo ON messages(conversation_id, timestamp)"
        )
        conn.commit()

def conversation_exists(conversation_id: int) -> bool:
    with _connect() as conn:  # or sqlite3.connect(...) if you're not using _connect()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM conversations WHERE id = ? LIMIT 1", (conversation_id,))
        return cur.fetchone() is not None
    

def create_conversation(title: str) -> int:
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO conversations (title) VALUES (?)", (title,))
        conn.commit()
        rowid = cur.lastrowid
        if rowid is None:
            # Defensive: this shouldn't happen in normal SQLite inserts
            raise RuntimeError("Failed to retrieve lastrowid after inserting conversation")
        return cast(int, rowid)


def add_message(conversation_id: int, sender: str, message: str, model: str) -> int:
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO messages (conversation_id, sender, message, model)
            VALUES (?, ?, ?, ?)
            """,
            (conversation_id, sender, message, model),
        )
        conn.commit()
        rowid = cur.lastrowid
        if rowid is None:
            raise RuntimeError("Failed to retrieve lastrowid after inserting message")
        return cast(int, rowid)



def get_conversation(conversation_id: int) -> List[sqlite3.Row]:
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM messages WHERE conversation_id = ? ORDER BY timestamp, id",
            (conversation_id,),
        )
        return cur.fetchall()


def list_conversations() -> List[sqlite3.Row]:
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, title, created_at FROM conversations ORDER BY created_at DESC, id DESC"
        )
        return cur.fetchall()


def update_conversation_title(conversation_id: int, title: str) -> None:
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE conversations SET title = ? WHERE id = ?",
            (title, conversation_id),
        )
        conn.commit()


# --- added helpers used by routers ---

def delete_message(message_id: int) -> int:
    """
    Delete a single message by id.
    Returns the number of rows deleted.
    """
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM messages WHERE id = ?", (message_id,))
        conn.commit()
        return cur.rowcount


def delete_conversation(conversation_id: int) -> Dict[str, int]:
    """
    Delete a conversation and all its messages.
    Returns counts of deleted rows.
    """
    with _connect() as conn:
        cur = conn.cursor()
        # Delete messages first to satisfy FK constraints if enforced.
        cur.execute(
            "DELETE FROM messages WHERE conversation_id = ?",
            (conversation_id,),
        )
        msg_count = cur.rowcount or 0
        cur.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
        conv_count = cur.rowcount or 0
        conn.commit()
        return {"conversations_deleted": conv_count, "messages_deleted": msg_count}


def get_recent_conversation_pairs(
    conversation_id: int, limit: int = 25
) -> List[Tuple[str, str]]:
    """
    Return up to ~limit user/assistant exchanges as (sender, message) tuples,
    ordered oldest → newest. Implemented by fetching ~2*limit most recent rows.
    """
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT sender, message
            FROM messages
            WHERE conversation_id = ?
            ORDER BY timestamp DESC, id DESC
            LIMIT ?
            """,
            (conversation_id, limit * 2),
        )
        rows = cur.fetchall()
        # Convert to simple tuples and flip to chronological order
        pairs = [(r["sender"], r["message"]) for r in rows][::-1]
        return pairs


def save_summarized_memory(conversation_id: int, text: str) -> str:
    """
    Persist a short memory/summary blob for a conversation.
    Returns the file path used.
    """
    mem_dir = os.path.join(os.path.dirname(__file__), "data", "memory")
    os.makedirs(mem_dir, exist_ok=True)
    path = os.path.join(mem_dir, f"convo_{conversation_id}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text.strip() + "\n")
    return path


# Initialize DB on module load
init_db()
