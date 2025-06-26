from dotenv import load_dotenv
import os


load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DB_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False  
    SECRET_KEY = '5b7c3a4f08d19e6e71fa0b9a2d389bhe' 
