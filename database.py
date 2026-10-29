"""Lab 5 SQLite user operations with first-run setup for Lab 7."""
import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).with_name('database.db')


def connect_to_db():
    return sqlite3.connect(DATABASE_PATH)


def create_db_table():
    conn = connect_to_db()
    try:
        table_exists = conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'users'"
        ).fetchone() is not None
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                country TEXT NOT NULL
            );
        ''')
        if not table_exists:
            # Preserve the initial user from the Lab 5 database on a fresh run.
            conn.execute(
                'INSERT INTO users (name, email, phone, address, country) VALUES (?, ?, ?, ?, ?)',
                ('Rita Abou Fares', 'rita@gmail.com', '067765434567', 'Beirut', 'Lebanon'),
            )
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


def insert_user(user):
    conn = connect_to_db()
    try:
        cur = conn.execute(
            'INSERT INTO users (name, email, phone, address, country) VALUES (?, ?, ?, ?, ?)',
            (user['name'], user['email'], user['phone'], user['address'], user['country']),
        )
        conn.commit()
        return get_user_by_id(cur.lastrowid)
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_users():
    conn = connect_to_db()
    try:
        conn.row_factory = sqlite3.Row
        return [dict(row) for row in conn.execute('SELECT * FROM users ORDER BY user_id').fetchall()]
    finally:
        conn.close()


def get_user_by_id(user_id):
    conn = connect_to_db()
    try:
        conn.row_factory = sqlite3.Row
        row = conn.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()
        return dict(row) if row is not None else {}
    finally:
        conn.close()


def update_user(user):
    conn = connect_to_db()
    try:
        conn.execute(
            'UPDATE users SET name = ?, email = ?, phone = ?, address = ?, country = ? WHERE user_id = ?',
            (user['name'], user['email'], user['phone'], user['address'], user['country'], user['user_id']),
        )
        conn.commit()
        return get_user_by_id(user['user_id'])
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


def delete_user(user_id):
    conn = connect_to_db()
    try:
        conn.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
        conn.commit()
        return {'status': 'User deleted successfully'}
    except sqlite3.Error:
        conn.rollback()
        return {'status': 'Cannot delete user'}
    finally:
        conn.close()


if __name__ == '__main__':
    create_db_table()
    print('User table created successfully')
