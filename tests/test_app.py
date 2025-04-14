import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Test that the home page loads successfully"""
    response = client.get('/')
    assert response.status_code == 200

def test_login_page(client):
    """Test that the login page loads successfully"""
    response = client.get('/login')
    assert response.status_code == 200

def test_admin_login(client):
    """Test admin login functionality"""
    response = client.post('/login', data={
        'email': 'admin@example.com',
        'password': 'admin123'
    }, follow_redirects=True)
    assert response.status_code == 200
    # Add more assertions based on your login success criteria

def test_student_login(client):
    """Test student login functionality"""
    response = client.post('/login', data={
        'email': 'student1@example.com',
        'password': 'student123'
    }, follow_redirects=True)
    assert response.status_code == 200
    # Add more assertions based on your login success criteria 