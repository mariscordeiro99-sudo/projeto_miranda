import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Cria ou atualiza um usuário administrador do Django usando variáveis de ambiente.'

    def handle(self, *args, **options):
        username = os.getenv('DJANGO_SUPERUSER_USERNAME', '').strip()
        email = os.getenv('DJANGO_SUPERUSER_EMAIL', '').strip()
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD', '')

        if not username:
            raise CommandError('DJANGO_SUPERUSER_USERNAME é obrigatório.')
        if not password:
            raise CommandError('DJANGO_SUPERUSER_PASSWORD é obrigatório.')

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email},
        )

        if email and user.email != email:
            user.email = email

        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()

        action = 'criado' if created else 'atualizado'
        self.stdout.write(self.style.SUCCESS(f'Usuário administrador "{username}" {action}.'))
