import os
from dotenv import load_dotenv

load_dotenv()

MB_APP_NAME = os.getenv("MB_APP_NAME", "BACKTRACK")
MB_APP_VERSION = os.getenv("MB_APP_VERSION", "0.1")
MB_CONTACT_EMAIL = os.getenv("MB_CONTACT_EMAIL", "no-reply@example.com")