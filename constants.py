import os
from dotenv import load_dotenv

load_dotenv()  # load variables from .env file

USERNAME = os.getenv("USERNAMES")
PASSWORD = os.getenv("PASSWORD")
MOBILE = os.getenv("MOBILE")
ORIGINAL_RESUME_PATH = os.getenv("ORIGINAL_RESUME_PATH")
MODIFIED_RESUME_PATH = os.getenv("MODIFIED_RESUME_PATH")
NAUKRI_LOGIN_URL = os.getenv("NAUKRI_LOGIN_URL")
NAUKRI_PROFILE_URL = os.getenv("NAUKRI_PROFILE_URL")
