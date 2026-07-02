from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

app = Flask(__name__)
CORS(app)


DB_CONFIG = {
    "host": "localhost",
    "database": "habit-tracker",      
    "user": "postgres",          
    "password": "24092005",  
    "port": "5432"
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

@app.route('/api/habits', methods=['GET'])
def get_habits():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM habits ORDER BY id ASC;")
        rows = cursor.fetchall()
        cursor.close()
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
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/habits', methods=['POST'])
def add_habit():
    try:
        data = request.json
        name = data.get('name')
        description = data.get('description', '')
        current_date = datetime.now().strftime("%d/%m/%Y")
        
        if not name:
            return jsonify({"error": "Missing name"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO habits (name, description, created_at) VALUES (%s, %s, %s)", 
            (name, description, current_date)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/habits/<int:habit_id>/toggle', methods=['POST'])
def toggle_habit(habit_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT completed_today, streak FROM habits WHERE id = %s;", (habit_id,))
        habit = cursor.fetchone()
        
        if not habit:
            cursor.close()
            conn.close()
            return jsonify({"error": "Not found"}), 404
            
        new_status = 1 if habit['completed_today'] == 0 else 0
        new_streak = habit['streak'] + 1 if new_status == 1 else max(0, habit['streak'] - 1)
        
        cursor.execute(
            "UPDATE habits SET completed_today = %s, streak = %s WHERE id = %s;",
            (new_status, new_streak, habit_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/habits/<int:habit_id>', methods=['DELETE'])
def delete_habit(habit_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM habits WHERE id = %s;", (habit_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)