# ToastyVotes Deployment Guide for Hostwinds

This comprehensive guide will walk you through deploying ToastyVotes to Hostwinds shared hosting with cPanel.

## Pre-Deployment Checklist

- [x] Complete Django application development
- [x] Configure proper settings for production
- [x] Create WSGI application entry points
- [x] Prepare static files for serving
- [x] Set up proper environment variables

## Deployment Step-by-Step Instructions

### 1. Prepare Your Local Project

Before uploading to Hostwinds, run these commands locally:

```powershell
# Collect static files
python manage.py collectstatic --noinput

# Create a production-ready .env file
Copy-Item .env.example .env
```

Edit the `.env` file with your production settings:
```
SECRET_KEY=your_secure_secret_key_here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### 2. Upload to Hostwinds

**Option 1: Using FTP**
1. Connect to your Hostwinds account via FTP (FileZilla recommended)
2. Upload the entire project directory to your chosen location (e.g., public_html)

**Option 2: Using Git (if supported)**
```powershell
# On Hostwinds server via SSH
cd ~/public_html
git clone https://your-repository-url.git
cd ToastyVotes_v2
```

### 3. Set Up Python Environment on Hostwinds

Most Hostwinds shared hosting plans use cPanel with Python support:

1. Log in to cPanel
2. Navigate to "Setup Python App" under Software section
3. Configure your application:
   - Python Version: 3.9+ (or highest available)
   - Application Root: /home/username/public_html/ToastyVotes_v2
   - Application URL: Your domain or subdomain
   - Application Entry Point: passenger_wsgi.py
   - Application Startup File: passenger_wsgi.py

4. Install dependencies:
```bash
pip install -r requirements.txt --user
```

### 4. Configure the Database

```bash
# Apply migrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser

# Create a platform admin
python manage.py create_platform_admin yourusername --create --password securepassword --email your@email.com
```

### 5. Configure Web Server (Apache)

The `.htaccess` file in your project root should already be properly configured:
- Routes non-static requests to your WSGI application
- Serves static and media files directly
- Implements security headers and browser caching

### 6. SSL Configuration

1. In cPanel, find "SSL/TLS Status" or similar
2. Install Let's Encrypt SSL certificate for your domain
3. Enable "Force HTTPS" to redirect all traffic to secure connections

### 7. Testing and Monitoring

After deployment:
1. Visit your domain to verify the site loads correctly
2. Test user registration and voting functionality
3. Check admin features like creating voting sessions
4. Monitor error logs in cPanel for any issues

## Hostwinds-Specific Configuration Notes

- **Memory Limits**: If you encounter memory issues, contact Hostwinds support to increase PHP memory limit
- **Cron Jobs**: Set up a daily cron job to clean expired sessions:
  ```
  0 0 * * * cd ~/public_html/ToastyVotes_v2 && python manage.py clearsessions
  ```
- **Backups**: Enable cPanel's automatic backup feature for both files and database

## Troubleshooting Common Issues

### Application Error 500
- Check error logs in cPanel
- Verify file permissions (755 for directories, 644 for files)
- Ensure all dependencies are installed correctly

### Static Files Not Loading
- Verify STATIC_ROOT and STATIC_URL settings
- Make sure collectstatic command ran successfully
- Check .htaccess rules for static file routing

### Database Connection Issues
- Ensure database configuration is correct in settings.py
- Check database user permissions

## Maintenance Recommendations

- Regularly backup your database through cPanel
- Update Django and dependencies when security updates are released
- Monitor your error logs for any issues

Remember that this guide is specific to Hostwinds shared hosting with cPanel. If you're using a different Hostwinds plan (like VPS), the deployment process may differ slightly.
