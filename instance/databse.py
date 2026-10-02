import sqlite3
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from datetime import datetime
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_TYPE = 'sqlite'
MONGO_URI = 'mongodb://localhost:27017/'
DB_NAME = 'plant_disease_db'
SQLITE_DB_PATH = 'plant_disease.db'

client = None
db = None

def get_db_connection():
    global client, db, DB_TYPE
    if DB_TYPE == 'mongodb' and db is not None:
        return db
    elif DB_TYPE == 'sqlite':
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    return None

def init_db():
    global client, db, DB_TYPE
    try:
        # Try MongoDB
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        db = client[DB_NAME]
        DB_TYPE = 'mongodb'
        logger.info("Connected to MongoDB successfully.")
        
        # Create admin if not exists
        admin_email = "admin@plantai.com"
        from werkzeug.security import generate_password_hash
        if db.users.find_one({"email": admin_email}) is None:
            db.users.insert_one({
                "id": str(uuid.uuid4()),
                "name": "Admin",
                "email": admin_email,
                "password_hash": generate_password_hash("admin123"),
                "role": "admin",
                "created_at": datetime.now()
            })
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.warning(f"MongoDB connection failed: {e}. Falling back to SQLite.")
        DB_TYPE = 'sqlite'
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create SQLite tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scans (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                image_filename TEXT NOT NULL,
                plant_name TEXT NOT NULL,
                disease_name TEXT NOT NULL,
                confidence REAL NOT NULL,
                treatment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        admin_email = "admin@plantai.com"
        cursor.execute("SELECT id FROM users WHERE email = ?", (admin_email,))
        if cursor.fetchone() is None:
            from werkzeug.security import generate_password_hash
            cursor.execute('''
                INSERT INTO users (id, name, email, password_hash, role, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (str(uuid.uuid4()), "Admin", admin_email, generate_password_hash("admin123"), "admin", datetime.now()))
        
        conn.commit()
        conn.close()

def create_user(name, email, password_hash):
    user_id = str(uuid.uuid4())
    created_at = datetime.now()
    if DB_TYPE == 'mongodb':
        db.users.insert_one({
            "id": user_id,
            "name": name,
            "email": email,
            "password_hash": password_hash,
            "role": "user",
            "created_at": created_at
        })
    else:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO users (id, name, email, password_hash, role, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, name, email, password_hash, "user", created_at))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return None
        conn.close()
    return user_id

def find_user_by_email(email):
    if DB_TYPE == 'mongodb':
        user = db.users.find_one({"email": email})
        if user:
            user['_id'] = str(user['_id'])
        return user
    else:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

def save_scan(user_id, image_filename, plant_name, disease_name, confidence, treatment):
    scan_id = str(uuid.uuid4())
    created_at = datetime.now()
    if DB_TYPE == 'mongodb':
        db.scans.insert_one({
            "id": scan_id,
            "user_id": user_id,
            "image_filename": image_filename,
            "plant_name": plant_name,
            "disease_name": disease_name,
            "confidence": confidence,
            "treatment": treatment,
            "created_at": created_at
        })
    else:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO scans (id, user_id, image_filename, plant_name, disease_name, confidence, treatment, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (scan_id, user_id, image_filename, plant_name, disease_name, confidence, treatment, created_at))
        conn.commit()
        conn.close()
    return scan_id

def get_user_scans(user_id):
    if DB_TYPE == 'mongodb':
        scans = list(db.scans.find({"user_id": user_id}, {'_id': 0}).sort("created_at", -1))
        return scans
    else:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scans WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

def get_all_scans():
    if DB_TYPE == 'mongodb':
        return list(db.scans.find({}, {'_id': 0}).sort("created_at", -1))
    else:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scans ORDER BY created_at DESC")
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

def get_admin_stats():
    stats = {
        "total_users": 0,
        "total_scans": 0,
        "disease_counts": {},
        "avg_confidence": 0.0
    }
    scans = get_all_scans()
    stats["total_scans"] = len(scans)
    
    if len(scans) > 0:
        total_conf = sum([s['confidence'] for s in scans])
        stats["avg_confidence"] = total_conf / len(scans)
        
        for s in scans:
            d_name = s['disease_name']
            stats["disease_counts"][d_name] = stats["disease_counts"].get(d_name, 0) + 1
            
    if DB_TYPE == 'mongodb':
        stats["total_users"] = db.users.count_documents({})
    else:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        stats["total_users"] = cursor.fetchone()[0]
        conn.close()
        
    return stats

def save_contact(name, email, message):
    contact_id = str(uuid.uuid4())
    created_at = datetime.now()
    if DB_TYPE == 'mongodb':
        db.contacts.insert_one({
            "id": contact_id,
            "name": name,
            "email": email,
            "message": message,
            "created_at": created_at
        })
    else:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO contacts (id, name, email, message, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (contact_id, name, email, message, created_at))
        conn.commit()
        conn.close()
    return contact_id

def get_all_users():
    if DB_TYPE == 'mongodb':
        users = list(db.users.find({}, {'_id': 0, 'password_hash': 0}).sort("created_at", -1))
        return users
    else:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, role, created_at FROM users ORDER BY created_at DESC")
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

def delete_user(user_id):
    if DB_TYPE == 'mongodb':
        db.users.delete_one({"id": user_id})
        db.scans.delete_many({"user_id": user_id})
    else:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM scans WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
    return True
