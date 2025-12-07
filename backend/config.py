import os
from dotenv import load_dotenv

load_dotenv()

# Get the absolute path of the directory where this script is located (backend/)
basedir = os.path.abspath(os.path.dirname(__file__))
# Navigate one level up to get the project's root directory
ROOT_DIR = os.path.join(basedir, '..')

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'a_very_secret_key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Define paths relative to the project root
    UPLOAD_FOLDER = os.path.join(ROOT_DIR, 'data')
    
    # Ensure the necessary directories exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(os.path.join(ROOT_DIR, 'db'), exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    # Correctly join the path for the SQLite database file in the root 'db' folder
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(ROOT_DIR, 'db', 'chatbot_dev.db')


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(ROOT_DIR, 'db', 'chatbot.db')

# Select the configuration to use
config = DevelopmentConfig