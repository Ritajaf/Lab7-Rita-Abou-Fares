"""One test for each of the ten graded Lab 7 requirements."""

import importlib
import sqlite3
import sys

import pytest

import database


@pytest.fixture
def database_path(tmp_path, monkeypatch):
    """Give every test its own database without changing database.db."""
    path = tmp_path / 'test_users.db'
    monkeypatch.setattr(database, 'DATABASE_PATH', path)
    return path


@pytest.fixture
def users_database(database_path):
    """Create the users table and the initial Lab 5 user."""
    database.create_db_table()
    return database


@pytest.fixture
def initial_user():
    """The user saved in the original Lab 5 database."""
    return {
        'user_id': 1,
        'name': 'Rita Abou Fares',
        'email': 'rita@gmail.com',
        'phone': '067765434567',
        'address': 'Beirut',
        'country': 'Lebanon',
    }


@pytest.fixture
def new_user():
    """The example input from the Lab 5 handout."""
    return {
        'name': 'John Doe',
        'email': 'jondoe@gamil.com',
        'phone': '067765434567',
        'address': 'John Doe Street, Innsbruck',
        'country': 'Austria',
    }


@pytest.fixture
def client(users_database):
    """Test Flask requests directly; no running server is needed."""
    from app import app

    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client


def test_database_created_with_specified_users_on_first_run(database_path, initial_user):
    assert not database_path.exists()

    # Execute exactly one app startup, even if a prior test imported it.
    if 'app' in sys.modules:
        importlib.reload(sys.modules['app'])
    else:
        importlib.import_module('app')

    assert database_path.is_file()
    with sqlite3.connect(database_path) as connection:
        columns = [row[1] for row in connection.execute('PRAGMA table_info(users)')]
        assert columns == ['user_id', 'name', 'email', 'phone', 'address', 'country']
        connection.row_factory = sqlite3.Row
        rows = connection.execute('SELECT * FROM users ORDER BY user_id').fetchall()
        assert [dict(row) for row in rows] == [initial_user]


def test_insert_user(users_database, initial_user, new_user):
    inserted = users_database.insert_user(new_user)

    assert inserted == dict(new_user, user_id=2)
    assert users_database.get_user_by_id(2) == inserted
    assert users_database.get_user_by_id(1) == initial_user


def test_get_users(users_database, initial_user, new_user):
    assert users_database.get_users() == [initial_user]
    inserted = users_database.insert_user(new_user)

    assert users_database.get_users() == [initial_user, inserted]


def test_get_users_by_id(users_database, initial_user, new_user):
    inserted = users_database.insert_user(new_user)

    assert users_database.get_user_by_id(initial_user['user_id']) == initial_user
    assert users_database.get_user_by_id(inserted['user_id']) == inserted


def test_update_user(users_database, initial_user, new_user):
    inserted = users_database.insert_user(new_user)
    updated = dict(
        inserted,
        name='John Doe Updated',
        email='john.updated@example.com',
        phone='0123456789',
        address='Hamra, Beirut',
        country='Lebanon',
    )

    assert users_database.update_user(updated) == updated
    assert users_database.get_user_by_id(inserted['user_id']) == updated
    assert users_database.get_user_by_id(1) == initial_user


def test_delete_user(users_database, initial_user, new_user):
    inserted = users_database.insert_user(new_user)

    result = users_database.delete_user(inserted['user_id'])

    assert result == {'status': 'User deleted successfully'}
    assert users_database.get_user_by_id(inserted['user_id']) == {}
    assert users_database.get_users() == [initial_user]


def test_api_get_user(client, initial_user, new_user):
    inserted = database.insert_user(new_user)

    response = client.get(f"/api/users/{inserted['user_id']}")

    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == inserted
    assert database.get_user_by_id(1) == initial_user


def test_api_add_user(client, initial_user, new_user):
    response = client.post('/api/users/add', json=new_user)
    expected = dict(new_user, user_id=2)

    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == expected
    assert database.get_users() == [initial_user, expected]

    downloaded = client.get('/api/users/2')
    assert downloaded.status_code == 200
    assert downloaded.get_json() == expected


def test_api_update_user(client, initial_user, new_user):
    inserted = database.insert_user(new_user)
    updated = dict(
        inserted,
        name='John Doe Updated',
        email='john.updated@example.com',
        phone='0123456789',
        address='Hamra, Beirut',
        country='Lebanon',
    )

    response = client.put('/api/users/update', json=updated)

    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == updated
    assert database.get_users() == [initial_user, updated]

    downloaded = client.get(f"/api/users/{inserted['user_id']}")
    assert downloaded.status_code == 200
    assert downloaded.get_json() == updated


def test_api_delete_user(client, initial_user, new_user):
    inserted = database.insert_user(new_user)

    response = client.delete(f"/api/users/delete/{inserted['user_id']}")

    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == {'status': 'User deleted successfully'}
    assert database.get_users() == [initial_user]
    assert database.get_user_by_id(inserted['user_id']) == {}

    downloaded = client.get(f"/api/users/{inserted['user_id']}")
    assert downloaded.status_code == 200
    assert downloaded.get_json() == {}
