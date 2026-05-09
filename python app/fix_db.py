import sqlite3

def fix_db():
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        # Check if otp_expiry exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'otp_expiry' not in columns:
            print("Adding otp_expiry column...")
            cursor.execute("ALTER TABLE users ADD COLUMN otp_expiry VARCHAR")
        else:
            print("otp_expiry column already exists.")
            
        if 'last_otp' not in columns:
            print("Adding last_otp column...")
            cursor.execute("ALTER TABLE users ADD COLUMN last_otp VARCHAR")
        else:
            print("last_otp column already exists.")
            
        conn.commit()
        conn.close()
        print("Database fix complete.")
    except Exception as e:
        print(f"Error fixing database: {e}")

if __name__ == "__main__":
    fix_db()
