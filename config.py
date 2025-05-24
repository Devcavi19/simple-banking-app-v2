import os
from urllib.parse import quote_plus

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    
    # Fix the password encoding
    DB_PASSWORD = "9YNB@y9mfP4=vx"  # Original password
    DB_PASSWORD_ENCODED = quote_plus(DB_PASSWORD)  # Properly encoded
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'mysql+pymysql://freedb_hecavi27:{DB_PASSWORD_ENCODED}@sql.freedb.tech:3306/freedb_simple_banking'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False