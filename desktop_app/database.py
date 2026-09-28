import sqlite3
import json
import os
import shutil
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).resolve().parent.parent / 'data'
DB_PATH = DATA_DIR / 'history.db'
PROCESSES_DIR = DATA_DIR / 'processes'

class HistoryDB:
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        PROCESSES_DIR.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processes (
                id TEXT PRIMARY KEY,
                created_at TEXT,
                status TEXT,
                shortage_files TEXT,
                warehouse_files TEXT,
                total_shortages INTEGER DEFAULT 0,
                matched_count INTEGER DEFAULT 0,
                not_found_count INTEGER DEFAULT 0,
                review_count INTEGER DEFAULT 0,
                output_file TEXT
            )
        ''')
        self.conn.commit()

    def get_next_id(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM processes ORDER BY id DESC LIMIT 1')
        row = cursor.fetchone()
        if row:
            last_id = row['id']
            try:
                num = int(last_id.split('-')[1]) + 1
            except:
                num = 1
            return f'PROC-{num:03d}'
        return 'PROC-001'

    def create_process(self, shortage_filenames: list[str], warehouse_filenames: list[str]) -> str:
        process_id = self.get_next_id()
        created_at = datetime.now().isoformat()
        status = 'processing'
        
        proc_dir = PROCESSES_DIR / process_id
        (proc_dir / 'input_shortages').mkdir(parents=True, exist_ok=True)
        (proc_dir / 'input_warehouses').mkdir(parents=True, exist_ok=True)
        (proc_dir / 'output').mkdir(parents=True, exist_ok=True)

        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO processes (id, created_at, status, shortage_files, warehouse_files)
            VALUES (?, ?, ?, ?, ?)
        ''', (process_id, created_at, status, json.dumps(shortage_filenames), json.dumps(warehouse_filenames)))
        self.conn.commit()
        return process_id

    def update_process(self, process_id, **kwargs):
        if not kwargs:
            return
        
        fields = []
        values = []
        for k, v in kwargs.items():
            fields.append(f"{k} = ?")
            values.append(v)
            
        values.append(process_id)
        
        query = f"UPDATE processes SET {', '.join(fields)} WHERE id = ?"
        cursor = self.conn.cursor()
        cursor.execute(query, tuple(values))
        self.conn.commit()

    def get_process(self, process_id) -> dict:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM processes WHERE id = ?', (process_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def get_all_processes(self) -> list[dict]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM processes ORDER BY created_at DESC')
        return [dict(row) for row in cursor.fetchall()]

    def mark_stuck_processes_as_failed(self):
        """Called on startup to clean up any processes that were running when the app was closed."""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE processes SET status = 'error' WHERE status = 'processing'")
        self.conn.commit()

    def delete_process(self, process_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM processes WHERE id = ?', (process_id,))
        self.conn.commit()
        
        proc_dir = self.get_process_dir(process_id)
        if proc_dir.exists():
            shutil.rmtree(proc_dir, ignore_errors=True)

    def get_process_dir(self, process_id) -> Path:
        return PROCESSES_DIR / process_id
