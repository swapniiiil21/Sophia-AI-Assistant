import sqlite3

DATABASE_NAME = "sophia.db"

def connect_db():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_NAME)
    return conn, conn.cursor()

def create_tables():
    """Creates necessary tables if they don't exist."""
    conn, cursor = connect_db()
    
    # Create sys_command table (assuming this is already handled, kept for completeness)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sys_command (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            path TEXT NOT NULL
        )
    ''')

    # Create web_command table (assuming this is already handled, kept for completeness)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS web_command (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            url TEXT NOT NULL
        )
    ''')

    # Create contacts table for WhatsApp messages by name
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            phone_number TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Call create_tables once when db.py is imported or run
create_tables()

# You can keep your testing module code if you wish, but it won't be used by the main app.
# Example:
# query = "OneNote"
# conn, cursor = connect_db() # Re-establish connection for testing if needed
# cursor.execute('SELECT path FROM sys_command WHERE name IN (?)', (query,))
# results = cursor.fetchall()
# print(results[0][0])
# conn.close()
