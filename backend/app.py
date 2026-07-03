from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta

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
        
        today_str = datetime.now().strftime("%d/%m/%Y")
        yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")
        
        habits = []
        for row in rows:
            habit_id = row["id"]
            completed_today = row["completed_today"]
            streak = row["streak"]
            last_updated = row["last_updated"] if row["last_updated"] else ""
            
            # LOGIC KIỂM TRA QUA NGÀY MỚI
            if last_updated and last_updated != today_str:
                if last_updated == yesterday_str:
                    # Nếu hôm qua làm rồi, nay sang ngày mới -> reset trạng thái Done về 0 để làm tiếp, GIỮ STREAK
                    completed_today = 0
                else:
                    # Nếu bỏ quên quá 1 ngày (không làm từ hôm kia) -> RESET CẢ STREAK VÀ DONE VỀ 0
                    completed_today = 0
                    streak = 0
                
                # Cập nhật trạng thái mới này ngầm vào database
                cursor.execute(
                    "UPDATE habits SET completed_today = %s, streak = %s WHERE id = %s;",
                    (completed_today, streak, habit_id)
                )
            
            habits.append({
                "id": habit_id,
                "name": row["name"],
                "description": row["description"] if row["description"] else "",
                "streak": streak,
                "completed_today": bool(completed_today),
                "created_at": row["created_at"] if row["created_at"] else "Chưa rõ"
            })
            
        conn.commit()
        cursor.close()
        conn.close()
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
            
        today_str = datetime.now().strftime("%d/%m/%Y")
        
        # Nếu đang ở trạng thái 0 (Chưa làm) -> Bấm thành Đã làm
        if habit['completed_today'] == 0:
            new_status = 1
            new_streak = habit['streak'] + 1
            last_update_val = today_str # Ghi nhận ngày làm là hôm nay
        else:
            # Nếu đang Đã làm -> Bấm hủy check (Uncheck)
            new_status = 0
            new_streak = max(0, habit['streak'] - 1)
            last_update_val = "" # Xóa ngày ghi nhận
        
        cursor.execute(
            "UPDATE habits SET completed_today = %s, streak = %s, last_updated = %s WHERE id = %s;",
            (new_status, new_streak, last_update_val, habit_id)
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