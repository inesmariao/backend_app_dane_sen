import os

def test_env_file_loaded():
    print("🔍 DB_NAME desde entorno:", os.environ.get('DB_NAME'))
    assert os.environ['DB_NAME'] == 'test_bd_app_encuesta1'