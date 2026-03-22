import pytest
import json
from app import app, db
from app.models import User, Class

@pytest.fixture
def client(monkeypatch):
    # Use in-memory SQLite for tests
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret'

    with app.app_context():
        db.create_all()
        # create an admin user
        admin = User(username='admin', email='admin@example.com', role='admin', full_name='Admin', is_active=True)
        admin.set_password('admin123')
        db.session.add(admin)
        # create a class
        cls = Class(name='Grade 1', section='A', academic_year='2024-25')
        db.session.add(cls)
        db.session.commit()

    with app.test_client() as client:
        yield client

def get_token(client, username='admin', password='admin123'):
    resp = client.post('/api/auth/login', json={'username': username, 'password': password})
    assert resp.status_code == 200
    data = resp.get_json()
    return data['access_token']

def test_create_list_update_delete_teacher(client):
    token = get_token(client)

    # Create teacher
    resp = client.post('/api/admin/teachers', json={
        'username': 'teacher1', 'email': 't1@example.com', 'password': 'pass', 'full_name': 'Teacher One', 'class_id': 1
    }, headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 201
    data = resp.get_json()
    teacher_id = data['teacher']['id']

    # List teachers
    resp = client.get('/api/admin/teachers', headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert any(t['username'] == 'teacher1' for t in data['teachers'])

    # Update teacher (change name and unassign class)
    resp = client.put(f'/api/admin/teachers/{teacher_id}', json={'full_name': 'Teacher 1 Updated', 'class_id': ''}, headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['teacher']['full_name'] == 'Teacher 1 Updated'

    # Delete teacher
    resp = client.delete(f'/api/admin/teachers/{teacher_id}', headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200

    # Ensure deleted
    resp = client.get('/api/admin/teachers', headers={'Authorization': f'Bearer {token}'})
    data = resp.get_json()
    assert not any(t['username'] == 'teacher1' for t in data['teachers'])
