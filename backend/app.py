from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Ép file dữ liệu CSDL luôn nằm chung thư mục với file app.py này
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "data.db")

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            streak INTEGER DEFAULT 0,
            completed_today INTEGER DEFAULT 0,
            created_at TEXT
        );
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/api/habits', methods=['GET'])
def get_habits():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM habits ORDER BY id ASC;")
    rows = cursor.fetchall()
    conn.close()
    
    habits = []
    for row in rows:
        habits.append({
            "id": row["id"],
            "name": row["name"],
            "description": row["description"] if row["description"] else "",
            "streak": row["streak"],
            "completed_today": bool(row["completed_today"]),
            "created_at": row["created_at"] if row["created_at"] else "Chưa rõ"
        })
    return jsonify(habits)

@app.route('/api/habits', methods=['POST'])
def add_habit():
    data = request.json
    name = data.get('name')
    description = data.get('description', '')
    current_date = datetime.now().strftime("%d/%m/%Y")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO habits (name, description, created_at) VALUES (?, ?, ?)", 
        (name, description, current_date)
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True}), 201

@app.route('/api/habits/<int:habit_id>/toggle', methods=['POST'])
def toggle_habit(habit_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT completed_today, streak FROM habits WHERE id = ?;", (habit_id,))
    habit = cursor.fetchone()
    
    if not habit:
        conn.close()
        return jsonify({"error": "Not found"}), 404
        
    new_status = 1 if habit['completed_today'] == 0 else 0
    new_streak = habit['streak'] + 1 if new_status == 1 else max(0, habit['streak'] - 1)
    
    cursor.execute(
        "UPDATE habits SET completed_today = ?, streak = ? WHERE id = ?;",
        (new_status, new_streak, habit_id)
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/api/habits/<int:habit_id>', methods=['DELETE'])
def delete_habit(habit_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM habits WHERE id = ?;", (habit_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)