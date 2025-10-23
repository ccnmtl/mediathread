from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


User = get_user_model()


class Command(BaseCommand):
    help = 'Creates test users for Cypress'

    def handle(self, *args, **options):
        User.objects.update_or_create(
            username='instructor_one',
            defaults={'is_staff': False, 'is_superuser': False},
        )
        user = User.objects.get(username='instructor_one')
        user.set_password('test')
        user.save()
        self.stdout.write(
            self.style.SUCCESS('Created test user instructor_one'))
