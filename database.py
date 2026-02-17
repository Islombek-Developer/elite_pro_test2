"""
Database module for Zakovati Elite Bot
SQLite implementation
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional


class Database:
    """Ma'lumotlar bazasi bilan ishlash klassi"""
    
    def __init__(self, db_file: str = "zakovati.db"):
        import os
        # Agar DATA_DIR berilgan bo'lsa, u papka mavjudligini tekshirish
        db_dir = os.path.dirname(os.path.abspath(db_file))
        if db_dir and db_dir != "/":
            os.makedirs(db_dir, exist_ok=True)
        self.db_file = db_file
    
    def get_connection(self):
        """Database connection olish"""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Ma'lumotlar bazasini yaratish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users jadvali
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                score INTEGER DEFAULT 0,
                is_admin INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Mavjud users jadvaliga is_admin ustunini qo'shish (migration)
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
        except Exception:
            pass
        
        # Game history jadvali
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                score INTEGER,
                subjects TEXT,
                played_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Sessions jadvali (login/logout uchun)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                user_id INTEGER PRIMARY KEY,
                is_logged_in INTEGER DEFAULT 1,
                logged_in_at TEXT DEFAULT CURRENT_TIMESTAMP,
                logged_out_at TEXT DEFAULT NULL
            )
        """)

        # Fanlar jadvali (admin tomonidan qo'shiladi)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                emoji TEXT DEFAULT '📘',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Savollar jadvali (admin tomonidan qo'shiladi)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS db_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer1 TEXT NOT NULL,
                answer2 TEXT NOT NULL,
                answer3 TEXT NOT NULL,
                answer4 TEXT NOT NULL,
                correct_index INTEGER NOT NULL,
                points INTEGER DEFAULT 10,
                subject TEXT NOT NULL,
                difficulty TEXT DEFAULT 'oson',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        print("✅ Database initialized successfully!")
    
    def add_user(self, user_id: int, username: str, password: str) -> bool:
        """Yangi foydalanuvchi qo'shish"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO users (user_id, username, password, score)
                VALUES (?, ?, ?, 0)
            """, (user_id, username, password))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Foydalanuvchi ma'lumotlarini olish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM users WHERE user_id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_all_users(self) -> List[Dict]:
        """Barcha foydalanuvchilarni olish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM users ORDER BY created_at DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def update_score(self, user_id: int, new_score: int) -> bool:
        """Foydalanuvchi ballini yangilash"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users SET score = ? WHERE user_id = ?
            """, (new_score, user_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating score: {e}")
            return False
    
    def get_top_users(self, limit: int = 10) -> List[Dict]:
        """Eng ko'p ball to'plagan foydalanuvchilar"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM users 
            ORDER BY score DESC 
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_statistics(self) -> Dict:
        """Umumiy statistika"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_users,
                SUM(score) as total_score,
                AVG(score) as avg_score,
                MAX(score) as max_score
            FROM users
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else {
            'total_users': 0,
            'total_score': 0,
            'avg_score': 0,
            'max_score': 0
        }
    
    def save_game_history(self, user_id: int, score: int, subjects: str) -> bool:
        """O'yin tarixini saqlash (ixtiyoriy)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO game_history (user_id, score, subjects)
                VALUES (?, ?, ?)
            """, (user_id, score, subjects))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving game history: {e}")
            return False
    
    def get_user_history(self, user_id: int) -> List[Dict]:
        """Foydalanuvchi o'yin tarixini olish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM game_history 
            WHERE user_id = ? 
            ORDER BY played_at DESC
        """, (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def delete_user(self, user_id: int) -> bool:
        """Foydalanuvchini o'chirish (admin)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
    
    def reset_all_scores(self) -> bool:
        """Barcha ballarni 0 ga qaytarish (admin)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("UPDATE users SET score = 0")
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error resetting scores: {e}")
            return False

    # ==================== SESSION (LOGIN/LOGOUT) ====================

    def login_user(self, user_id: int) -> bool:
        """Foydalanuvchini tizimga kirish (login)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO sessions (user_id, is_logged_in, logged_in_at, logged_out_at)
                VALUES (?, 1, ?, NULL)
                ON CONFLICT(user_id) DO UPDATE SET
                    is_logged_in = 1,
                    logged_in_at = excluded.logged_in_at,
                    logged_out_at = NULL
            """, (user_id, now))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error login user: {e}")
            return False

    def logout_user(self, user_id: int) -> bool:
        """Foydalanuvchini tizimdan chiqarish (logout)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO sessions (user_id, is_logged_in, logged_out_at)
                VALUES (?, 0, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    is_logged_in = 0,
                    logged_out_at = excluded.logged_out_at
            """, (user_id, now))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error logout user: {e}")
            return False

    def is_logged_in(self, user_id: int) -> bool:
        """Foydalanuvchi tizimda ekanligini tekshirish"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT is_logged_in FROM sessions WHERE user_id = ?
            """, (user_id,))
            row = cursor.fetchone()
            conn.close()
            if row is None:
                return False
            return bool(row['is_logged_in'])
        except Exception as e:
            print(f"Error checking session: {e}")
            return False

    def verify_password(self, user_id: int, password: str) -> bool:
        """Parolni tekshirish (login uchun)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT password FROM users WHERE user_id = ?
        """, (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row is None:
            return False
        return row['password'] == password

    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Username bo'yicha foydalanuvchini topish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM users WHERE username = ?
        """, (username,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
        return None

    # ==================== FANLAR (SUBJECTS) ====================

    def add_subject(self, name: str, emoji: str = '📘') -> bool:
        """Yangi fan qo'shish"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO subjects (name, emoji) VALUES (?, ?)
            """, (name.strip(), emoji.strip()))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            print(f"Error adding subject: {e}")
            return False

    def get_all_subjects_db(self) -> List[Dict]:
        """Barcha fanlarni DB dan olish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM subjects ORDER BY name")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def delete_subject(self, name: str) -> bool:
        """Fanni o'chirish"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM subjects WHERE name = ?", (name,))
            cursor.execute("DELETE FROM db_questions WHERE subject = ?", (name,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting subject: {e}")
            return False

    # ==================== SAVOLLAR (QUESTIONS) ====================

    def add_question(self, question: str, answers: list, correct_index: int,
                     subject: str, difficulty: str, points: int) -> bool:
        """Yangi savol qo'shish"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO db_questions 
                (question, answer1, answer2, answer3, answer4, correct_index, points, subject, difficulty)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (question, answers[0], answers[1], answers[2], answers[3],
                  correct_index, points, subject, difficulty))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding question: {e}")
            return False

    def get_questions_by_subject_db(self, subject: str) -> List[Dict]:
        """Fan bo'yicha savollarni DB dan olish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM db_questions WHERE subject = ? 
            ORDER BY CASE difficulty
                WHEN 'oson' THEN 1
                WHEN 'o''rta' THEN 2
                WHEN 'qiyin' THEN 3
                WHEN 'juda_qiyin' THEN 4
                ELSE 1 END
        """, (subject,))
        rows = cursor.fetchall()
        conn.close()
        result = []
        for row in rows:
            d = dict(row)
            result.append({
                'id': d['id'],
                'q': d['question'],
                'a': [d['answer1'], d['answer2'], d['answer3'], d['answer4']],
                'c': d['correct_index'],
                'p': d['points'],
                'f': d['subject'],
                'd': d['difficulty']
            })
        return result

    def get_all_questions_db(self) -> List[Dict]:
        """Barcha savollarni DB dan olish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM db_questions ORDER BY subject, difficulty")
        rows = cursor.fetchall()
        conn.close()
        result = []
        for row in rows:
            d = dict(row)
            result.append({
                'id': d['id'],
                'q': d['question'],
                'a': [d['answer1'], d['answer2'], d['answer3'], d['answer4']],
                'c': d['correct_index'],
                'p': d['points'],
                'f': d['subject'],
                'd': d['difficulty']
            })
        return result

    def delete_question(self, question_id: int) -> bool:
        """Savol o'chirish"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM db_questions WHERE id = ?", (question_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting question: {e}")
            return False

    def get_total_questions_db(self) -> int:
        """Jami savollar soni (DB)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM db_questions")
        row = cursor.fetchone()
        conn.close()
        return row['cnt'] if row else 0

    def get_subjects_stats_db(self) -> Dict:
        """Fanlar bo'yicha savol statistikasi (DB)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT subject, COUNT(*) as cnt FROM db_questions GROUP BY subject
        """)
        rows = cursor.fetchall()
        conn.close()
        return {row['subject']: row['cnt'] for row in rows}

    # ==================== ADMIN FILTR (reyting va statistika uchun) ====================

    def get_top_users_no_admin(self, limit: int = 10) -> List[Dict]:
        """Adminlarsiz TOP foydalanuvchilar"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM users WHERE is_admin = 0
            ORDER BY score DESC LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_all_users_no_admin(self) -> List[Dict]:
        """Adminlarsiz barcha foydalanuvchilar"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM users WHERE is_admin = 0 ORDER BY created_at DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_statistics_no_admin(self) -> Dict:
        """Adminlarsiz umumiy statistika"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as total_users,
                COALESCE(SUM(score), 0) as total_score,
                COALESCE(AVG(score), 0) as avg_score,
                COALESCE(MAX(score), 0) as max_score
            FROM users WHERE is_admin = 0
        """)
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else {
            'total_users': 0, 'total_score': 0, 'avg_score': 0, 'max_score': 0
        }

    def set_admin_flag(self, user_id: int, is_admin: int = 1) -> bool:
        """Foydalanuvchiga admin belgisi qo'yish"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET is_admin = ? WHERE user_id = ?", (is_admin, user_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error set admin flag: {e}")
            return False

    def get_all_admins(self) -> List[Dict]:
        """Barcha adminlarni olish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE is_admin = 1 ORDER BY created_at")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def promote_to_admin(self, user_id: int) -> bool:
        """Foydalanuvchini admin qilish"""
        return self.set_admin_flag(user_id, 1)

    def demote_from_admin(self, user_id: int) -> bool:
        """Adminni oddiy foydalanuvchiga qaytarish"""
        return self.set_admin_flag(user_id, 0)

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """ID bo'yicha foydalanuvchini topish"""
        return self.get_user(user_id)

    def search_user(self, query: str) -> List[Dict]:
        """Foydalanuvchini ism yoki ID bo'yicha qidirish"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            user_id = int(query)
            cursor.execute("SELECT * FROM users WHERE user_id = ? OR username LIKE ?",
                           (user_id, f"%{query}%"))
        except ValueError:
            cursor.execute("SELECT * FROM users WHERE username LIKE ?", (f"%{query}%",))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


# Test uchun
if __name__ == "__main__":
    db = Database()
    db.init_db()
    print("Database test passed!")
