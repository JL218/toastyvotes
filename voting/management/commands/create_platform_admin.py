from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from voting.models import AdminProfile


class Command(BaseCommand):
    help = 'Creates or updates a user as a platform admin for ToastyVotes'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the user to make admin')
        parser.add_argument('--create', action='store_true', help='Create the user if it does not exist')
        parser.add_argument('--password', type=str, help='Password for new user if created')
        parser.add_argument('--email', type=str, help='Email for new user if created')

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            user = User.objects.get(username=username)
            self.stdout.write(f'User "{username}" found.')
            
            # Check if admin profile exists, create if not
            admin_profile, created = AdminProfile.objects.get_or_create(user=user)
            
            if created or not admin_profile.is_platform_admin:
                admin_profile.is_platform_admin = True
                admin_profile.save()
                self.stdout.write(self.style.SUCCESS(f'User "{username}" has been made a platform admin.'))
            else:
                self.stdout.write(f'User "{username}" is already a platform admin.')
                
        except User.DoesNotExist:
            if options['create']:
                if not options['password']:
                    raise CommandError('--password is required when creating a new user')
                
                # Create user
                email = options['email'] or ''
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=options['password']
                )
                
                # Create admin profile
                AdminProfile.objects.create(user=user, is_platform_admin=True)
                
                self.stdout.write(self.style.SUCCESS(
                    f'User "{username}" has been created and made a platform admin.'
                ))
            else:
                raise CommandError(f'User "{username}" does not exist. Use --create to make a new user.')
