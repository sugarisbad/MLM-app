import secrets
from dotenv import load_dotenv
import os

load_dotenv()

# Генерация нового секретного ключа
def generate_secret_key():
    return secrets.token_hex(32)

# Сохранение в .env файл
if not os.getenv('SECRET_KEY'):
    with open('.env', 'a') as f:
        f.write(f"\nSECRET_KEY={generate_secret_key()}\n")
    print("Новый SECRET_KEY успешно сгенерирован и сохранён в .env")
else:
    print("SECRET_KEY уже существует в .env")