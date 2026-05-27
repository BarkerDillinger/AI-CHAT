# File: chat/conversation.py

import os
import sqlite3
from typing import List, Tuple, Dict, Any, Optional, cast

# --- configuration -----------------------------------------------------------

DB_KEY = os.getenv("CHAT_DB_KEY")  # set this to enable SQLCipher
# If encryption is enabled, default to a new encrypted file so we never clobber
# the plaintext DB accidentally.
DEFAULT_DB_NAME = "conversation_memory.enc.db" if DB_KEY else "conversation_memory.db"
DB_FILE = os.getenv(
    "CHAT_DB_FILE",
    os.path.join(os.path.dirname(__file__), "data", DEFAULT_DB_NAME),
)

# Ensure the directory exists
os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)

_sqlcipher_mod: Any = None  # late import holder (typed Any to appease Pylance)


# --- utilities ---------------------------------------------------------------

def _escape_single_quotes(s: str) -> str:
    return s.replace("'", "''")


def _hybrid_row(cursor, row):
    """
    Row factory that supports BOTH name *and* index access.

    Example:
      r = fetched_row
      r["sender"] -> ok (by column name)
      r[0]        -> ok (by index)
    """
    out: Dict[Any, Any] = {}
    for i, col in enumerate(cursor.description):
        out[i] = row[i]
        out[col[0]] = row[i]
    return out


def _connect():
    """
    Return a DB connection:
      - SQLCipher (encrypted) if CHAT_DB_KEY is set
      - sqlite3 (plaintext) otherwise

    Row access:
      - encrypted path -> _hybrid_row (works with pysqlcipher3 cursor)
      - plaintext path -> sqlite3.Row
    """
    global _sqlcipher_mod

    if DB_KEY:
        # Encrypted (SQLCipher) path
        try:
            from pysqlcipher3 import dbapi2 as sqlcipher  # type: ignore
            _sqlcipher_mod = sqlcipher  # type: ignore[assignment]
        except Exception as e:
            raise RuntimeError(
                "CHAT_DB_KEY is set but pysqlcipher3 is not available. "
                "Install system SQLCipher and `pip install pysqlcipher3`."
            ) from e

        conn = _sqlcipher_mod.connect(DB_FILE)
        # Apply key
        conn.execute(f"PRAGMA key = '{_escape_single_quotes(DB_KEY)}';")

        # These PRAGMAs are best-effort; ignore if your SQLCipher build lacks them.
        try:
            conn.execute("PRAGMA cipher_compatibility = 4;")  # SQLCipher 4+
        except Exception:
            pass
        try:
            conn.execute("PRAGMA kdf_iter = 256000;")
        except Exception:
            pass

        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = _hybrid_row  # IMPORTANT: not sqlite3.Row here
        return conn

    # Plain sqlite path
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


# --- schema / init -----------------------------------------------------------

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
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_messages_convo ON messages(conversation_id, timestamp)"
        )
        conn.commit()


# --- CRUD helpers ------------------------------------------------------------

def create_conversation(title: str) -> int:
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO conversations (title) VALUES (?)", (title,))
        conn.commit()
        rowid = cur.lastrowid
        if rowid is None:
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


def get_conversation(conversation_id: int):
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM messages WHERE conversation_id = ? ORDER BY timestamp, id",
            (conversation_id,),
        )
        return cur.fetchall()


def list_conversations():
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


def delete_message(message_id: int) -> int:
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM messages WHERE id = ?", (message_id,))
        conn.commit()
        return int(cur.rowcount or 0)


def delete_conversation(conversation_id: int) -> Dict[str, int]:
    with _connect() as conn:
        cur = conn.cursor()
        # messages first (FK-friendly)
        cur.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
        msg_count = int(cur.rowcount or 0)
        cur.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
        conv_count = int(cur.rowcount or 0)
        conn.commit()
        return {"conversations_deleted": conv_count, "messages_deleted": msg_count}


def get_recent_conversation_pairs(conversation_id: int, limit: int = 25) -> List[Tuple[str, str]]:
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
        pairs = [(r["sender"], r["message"]) for r in rows][::-1]
        return pairs


def save_summarized_memory(conversation_id: int, text: str) -> str:
    mem_dir = os.path.join(os.path.dirname(__file__), "data", "memory")
    os.makedirs(mem_dir, exist_ok=True)
    path = os.path.join(mem_dir, f"convo_{conversation_id}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text.strip() + "\n")
    return path


def conversation_exists(conversation_id: int) -> bool:
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM conversations WHERE id = ? LIMIT 1", (conversation_id,))
        return cur.fetchone() is not None


# Initialize on import
init_db()
