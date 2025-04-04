import mysql.connector
from mysql.connector import Error, MySQLConnection
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional, Dict, Tuple

class MySQLDatabase:
    def __init__(self, host: str, database: str, user: str, password: str):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection: Optional[MySQLConnection] = None
        self.ssl_disabled = True  # Set based on your server configuration

        # Establish connection before table creation
        if self.connect():
            self.create_users_table()
        else:
            print("Database connection failed. Exiting.")

    def connect(self) -> bool:
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                ssl_disabled=self.ssl_disabled
            )
            if self.connection.is_connected():
                print("✅ Connected to MySQL Database!")
                return True
        except Error as e:
            print(f"❌ Connection error: {e}")
        return False

    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🔌 Disconnected from database.")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def create_users_table(self):
        """Create users table if it does not exist"""
        if not self.table_exists('users'):
            query = """
            CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(256) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            self.execute_query(query)

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database"""
        query = """
        SELECT COUNT(*) AS count
        FROM information_schema.tables
        WHERE table_schema = %s AND table_name = %s
        """
        result = self.fetch_one(query, (self.database, table_name))
        return result["count"] > 0 if result else False

    def execute_query(self, query: str, params: tuple = None) -> bool:
        """Execute a write query"""
        if not self.connection or not self.connection.is_connected():# new code 
        # Reconnect if the connection is closed
            self.connect() #new code 
        if not self.connection:
            print("❌ No database connection!")
            return False
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params or ())
                self.connection.commit()
                return True
        except Error as e:
            print(f"❌ Query error: {e}")
            self.connection.rollback()
            return False

    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict]:
        """Execute a read query and return single result"""
        if not self.connection:
            print("❌ No database connection!")
            return None
        try:
            with self.connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchone()
        except Error as e:
            print(f"❌ Fetch error: {e}")
            return None

    def register_user(self, username: str, email: str, password: str) -> Tuple[bool, str]:
        """Register a new user with password hashing"""
        if self.fetch_one("SELECT id FROM users WHERE email = %s", (email,)):
            return False, "⚠️ Email already registered"

        password_hash = generate_password_hash(password)
        success = self.execute_query(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            (username, email, password_hash)
        )
        return success, "✅ Registration successful" if success else "❌ Registration failed"

    def login_user(self, email: str, password: str) -> Tuple[bool, Dict]:
        """Authenticate user with email and password"""
        user = self.fetch_one(
            "SELECT id, username, email, password_hash FROM users WHERE email = %s",
            (email,)
        )
        if not user:
            return False, {"error": "⚠️ User not found"}
        
        if check_password_hash(user['password_hash'], password):
            return True, {"id": user['id'], "username": user['username'], "email": user['email']}
        
        return False, {"error": "❌ Invalid password"}

# Example Usage
if __name__ == "__main__":
    db_config = {
        'host': 'localhost',
        'database': 'medical_app',
        'user': 'root',
        'password': ''
    }

    with MySQLDatabase(**db_config) as db:
        print("\n🔹 Testing Registration")
        success, message = db.register_user("john_doe", "john@example.com", "SecurePass123!")
        print(f"{message}")
        
        print("\n🔹 Testing Duplicate Registration")
        success, message = db.register_user("john_doe", "john@example.com", "SecurePass123!")
        print(f"{message}")
        
        print("\n🔹 Testing Valid Login")
        success, user_data = db.login_user("john@example.com", "SecurePass123!")
        print(f"Login: {success} - {user_data}")
        
        print("\n🔹 Testing Invalid Password")
        success, user_data = db.login_user("john@example.com", "WrongPassword")
        print(f"Login: {success} - {user_data}")
        
        print("\n🔹 Testing Non-Existent User")
        success, user_data = db.login_user("nonexistent@example.com", "Password123")
        print(f"Login: {success} - {user_data}")