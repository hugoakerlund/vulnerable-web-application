# FIX 4: Use Django's built-in password hashing for better security
# from django.contrib.auth.hashers import make_password
from django.db import migrations

from ..utils import hash_password


def seed_initial_users_and_accounts(apps, schema_editor):
    Account = apps.get_model('pages', 'Account')
    User = apps.get_model('auth', 'User')

    user_data = [
        ('bob', 'squarepants', 1000, 'FI1110000001111111'),
        ('alice', 'redqueen', 2000, 'FI1110000002222222'),
        ('admin', 'admin', 3000, 'FI1110000003333333'),
    ]

    for username, password, balance, iban in user_data:
        user, created = User.objects.get_or_create(
            username=username,

            # FLAW 4: Cryptographic failure - Password is hashed insecurely
            defaults={'password': hash_password(password)},

            # FIX 4: Use Django's built-in password hashing for better security
            # defaults={'password': make_password(password)},
        )
        if not created:

            # FLAW 4: Cryptographic failure - Password is hashed insecurely
            user.password = hash_password(password)

            # FIX 4: Use Django's built-in password hashing for better security
            # user.password = make_password(password)

            user.save(update_fields=['password'])
        Account.objects.get_or_create(owner=user, iban=iban, defaults={'balance': balance})


def reverse_seed(apps, schema_editor):
    Account = apps.get_model('pages', 'Account')
    User = apps.get_model('auth', 'User')
    Account.objects.filter(iban__in=[
        'FI1110000001111111',
        'FI1110000002222222',
        'FI1110000003333333',
    ]).delete()
    User.objects.filter(username__in=['bob', 'alice', 'admin']).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('pages', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(seed_initial_users_and_accounts, reverse_seed),
    ]
