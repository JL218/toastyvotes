import os
import sys
import django
from pathlib import Path

# Get the absolute path of the current script
SCRIPT_DIR = Path(__file__).resolve().parent

# Add the project directory to the Python path
sys.path.insert(0, str(SCRIPT_DIR))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toastyvotes.settings')
django.setup()

# Now import Django models after django.setup()
from django.contrib.auth.models import User
from voting.models import AdminProfile

def create_superuser():
    """Create a Django superuser"""
    username = 'admin'
    email = 'admin@example.com'
    password = 'toastyvotes@2025'  # Use a strong password in production!
    
    # Check if user already exists
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        user.set_password(password)
        user.save()
        print(f"Reset password for existing superuser: {username}")
    else:
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"Created new superuser: {username}")
    
    return username

def create_platform_admin(username):
    """Make user a platform admin"""
    try:
        user = User.objects.get(username=username)
        
        # Create or update admin profile
        admin_profile, created = AdminProfile.objects.get_or_create(user=user)
        admin_profile.is_platform_admin = True
        admin_profile.save()
        
        action = "Created new" if created else "Updated existing"
        print(f"{action} platform admin for user: {username}")
        
    except User.DoesNotExist:
        print(f"User {username} does not exist")

if __name__ == "__main__":
    username = create_superuser()
    create_platform_admin(username)
    print("\nCredentials:")
    print("Username: admin")
    print("Password: toastyvotes@2025")
    print("\nYou can now access:")
    print("- Django admin at /admin/")
    print("- ToastyVotes platform at / (login with the same credentials)")
