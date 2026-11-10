"""Create a login for the site owner.

    uv run python manage.py add_editor lyndsay lyndsay@example.com

You'll be asked to type a password. She can change it later from her account
page in the admin, or use "Forgot password?" once email is set up.
"""

import getpass

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create a 'Site owner' login that can edit pages, images, blog posts and testimonials."

    def add_arguments(self, parser):
        parser.add_argument("username")
        parser.add_argument("email")
        parser.add_argument("--first-name", default="")
        parser.add_argument(
            "--password-env",
            help="Read the password from this environment variable instead of prompting.",
        )

    def handle(self, username, email, first_name="", password_env=None, **opts):
        import os

        User = get_user_model()
        if User.objects.filter(username=username).exists():
            raise CommandError(f"User '{username}' already exists.")
        try:
            group = Group.objects.get(name="Site owner")
        except Group.DoesNotExist:
            raise CommandError("Run `manage.py seed_site` first to create the Site owner group.")

        if password_env:
            password = os.environ.get(password_env) or ""
        else:
            password = getpass.getpass("Password: ")
            if password != getpass.getpass("Password (again): "):
                raise CommandError("Passwords didn't match.")
        user = User(username=username, email=email, first_name=first_name)
        try:
            validate_password(password, user)
        except ValidationError as e:
            raise CommandError(" ".join(e.messages))
        user.set_password(password)
        user.save()
        user.groups.add(group)
        self.stdout.write(self.style.SUCCESS(f"Created '{username}'. Log in at /admin/."))
