# ToDoApp/test/test_users.py
from fastapi import status
from .utils import *
from ..routers.users import get_db
# Override get_current_user from the auth module where it originates!
from ..routers.auth import get_current_user 

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_return_user(test_user):
    # Hit the correct absolute route path based on prefix + endpoint name
    response = client.get("/user/get_user")
    
    assert response.status_code == status.HTTP_200_OK
    
    # Note: If your testing database is fresh/empty, this will return None/null. 
    # If it fails here, you can seed a test user in a fixture just like you did for todos!
    assert response.json()['username'] == 'codingwithOla'
    assert response.json()['email'] == 'oladokunolamide@gmail.com'
    assert response.json()['first_name'] == 'Olamide'
    assert response.json()['last_name'] == 'Oladokun'
    assert response.json()['role'] == 'admin'
    assert response.json()['phone_number'] == '(234)-234-1111'


def test_change_password_success(test_user):
    request_data = {
        'password': 'testpassword',
        'new_password': 'newsecurepassword'
    }
    
    response = client.put("/user/password", json=request_data)
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify that the password has been changed in the database
    db = TestingSessionLocal()
    user_model = db.query(Users).filter(Users.id == 1).first()
    assert bcrypt_context.verify('newsecurepassword', user_model.hashed_password)


def test_change_password_invalid_current_password(test_user):
    request_data = {
        'password': 'wrongpassword',
        'new_password': 'newsecurepassword'
    }
    
    response = client.put("/user/password", json=request_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Error on password change'}

def test_change_phone_number_success(test_user):
    new_phone_number = "(234)-234-5678"
    
    response = client.put(f"/user/phone_number/{new_phone_number}")
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify that the phone number has been changed in the database
    db = TestingSessionLocal()
    user_model = db.query(Users).filter(Users.id == 1).first()
    assert user_model.phone_number == new_phone_number