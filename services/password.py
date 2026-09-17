from pwdlib import PasswordHash

password_hasher = PasswordHash.recommended()


def hash_password(password):
    return password_hasher.hash(password) # hash() -passsword secure


def verify_password(password, hashed_password): # verify -- enter password check with hash password 
    return password_hasher.verify(
        password,
        hashed_password
    )