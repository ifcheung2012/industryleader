# settings.py
import os
from os.path import join, dirname
from dotenv import load_dotenv

# dotenv_path = join(dirname(__file__), os.getenv("ENVIRONMENT_FILE"))
load_dotenv(override=True)

APP_HOST = os.environ.get("HOST")
APP_PORT = int(os.environ.get("PORT"))
APP_DEBUG = bool(os.environ.get("DEBUG"))
DEV_TOOLS_PROPS_CHECK = bool(os.environ.get("DEV_TOOLS_PROPS_CHECK"))

MYSQL_USER=os.environ.get("MYSQL_USER")
MYSQL_PASSWORD=os.environ.get("MYSQL_PASSWORD")
MYSQL_HOST=os.environ.get("MYSQL_HOST")
MYSQL_PORT=int(os.environ.get("MYSQL_PORT"))
MYSQL_DATABASE=os.environ.get("MYSQL_DATABASE")


if __name__ == '__main__':
    print(MYSQL_PASSWORD)
