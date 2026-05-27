from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    """
    Custom management command: python manage.py seed_users

    Django management commands are how you write admin scripts that
    have access to the full Django environment (database, settings, models).
    This is the Django-idiomatic way to seed data — not hardcoding it in views.
    """
    help = 'Seeds the database with default rep and supervisor users'

    def handle(self, *args, **options):
        users_to_create = [
            {
                'username': 'rep',
                'password': 'rep123',
                'role': User.ROLE_REP,
                'email': 'rep@retailos.com',
            },
            {
                'username': 'supervisor',
                'password': 'super123',
                'role': User.ROLE_SUPERVISOR,
                'email': 'supervisor@retailos.com',
            },
        ]

        for user_data in users_to_create:
            username = user_data['username']

            if User.objects.filter(username=username).exists():
                self.stdout.write(f'  User "{username}" already exists — skipping.')
                continue

            # create_user() handles password hashing automatically
            # NEVER store plain-text passwords — Django's create_user does bcrypt for you
            user = User.objects.create_user(
                username=username,
                password=user_data['password'],
                role=user_data['role'],
                email=user_data['email'],
            )
            self.stdout.write(
                self.style.SUCCESS(f'  Created user: {user.username} (role: {user.role})')
            )

        self.stdout.write(self.style.SUCCESS('Seeding complete.'))