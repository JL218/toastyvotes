from django.core.management.utils import get_random_secret_key
import os

def generate_key():
    """Generate a secure secret key for Django settings"""
    # Generate a secure random key
    secret_key = get_random_secret_key()
    print("\nGenerated Django SECRET_KEY:")
    print("-" * 50)
    print(secret_key)
    print("-" * 50)
    print("\nFor your .env file:")
    print('SECRET_KEY=' + secret_key)
    print("\nKeep this key secure and don't share it publicly!")

if __name__ == "__main__":
    generate_key()
    input()
