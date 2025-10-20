#!/usr/bin/env python
"""
Script para generar una clave secreta segura para Django en producción
"""
import secrets
import string

def generate_secret_key(length=50):
    """Generar clave secreta segura para Django"""
    characters = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    secret_key = ''.join(secrets.choice(characters) for _ in range(length))
    return secret_key

if __name__ == '__main__':
    print("🔐 Generando clave secreta para Django...")
    secret_key = generate_secret_key()
    print(f"\n📋 Tu clave secreta es:")
    print(f"SECRET_KEY={secret_key}")
    print(f"\n⚠️  IMPORTANTE: Guarda esta clave de forma segura.")
    print(f"⚠️  NUNCA la compartas públicamente.")
    print(f"\n💡 Usa esta clave en tu variable de entorno SECRET_KEY en Render.")