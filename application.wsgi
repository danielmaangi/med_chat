import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add your application directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import your Flask app
from app import app as application 