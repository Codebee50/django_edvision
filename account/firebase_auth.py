from firebase_admin import auth

from account.models import UserAccount

def verify_firebase_token(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        return None
    
def get_or_create_user_from_firebase(decoded_token:dict):
    
    print("the decoded token is", decoded_token)
    email = decoded_token.get('email')
    
    if not email:
        raise ValueError("Email not found in firebase token")
    
    if not decoded_token.get("email_verified", False):
        raise ValueError("Email has not been verified by google")
    
    created=False
    try:
        user = UserAccount.objects.get(email=email)
    except UserAccount.DoesNotExist:
        import uuid
        
        random_password = str(uuid.uuid4())
        
        full_name = decoded_token.get('name', '')
        name_parts = full_name.strip().split()
        if len(name_parts) == 0:
            first_name = full_name
            last_name = ''
        elif len(name_parts) == 1:
            first_name = name_parts[0]
            last_name = ''
        else:
            first_name = name_parts[0]
            last_name = ' '.join(name_parts[1:])
        
        user = UserAccount.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            email = decoded_token.get('email'),
            password=random_password,
            email_verified = True
        )
        created= True
        
    return user, created