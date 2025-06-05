import dotenv
import os
from pathlib import Path

def pytest_configure():
    dotenv.load_dotenv(dotenv_path=Path(__file__).parent / ".env.test", override=True)
