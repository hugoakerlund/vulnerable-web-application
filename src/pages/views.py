from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.db import connection, transaction
from django.shortcuts import redirect, render

from .models import Account
from .utils import hash_password, authenticate_user


def addAccountView(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':

        iban = request.POST.get('iban', '').strip()

        # FIX 1: Validate the IBAN format before processing it to prevent SQL injection
        # if not check_iban_format(iban):
        #     return render(request, 'pages/add_account.html', {'error': 'ERROR: Invalid IBAN format.'})

        if iban:
            # FAULT 1: SQL injection - The following code is vulnerable to SQL injection because it directly concatenates user input into the SQL query without proper sanitization or parameterization.
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO pages_account (owner_id, iban, balance) VALUES (" + str(request.user.id) + ", '" + iban + "', 0)"
                )

            # FIX 1: Use parameterized queries to prevent SQL injection
            # with connection.cursor() as cursor:
            #     cursor.execute(
            #         "INSERT INTO pages_account (owner_id, iban, balance) VALUES (%s, %s, 0)",
            #         (request.user.id, iban)
            #     )

        return redirect('home')

    else:
        return render(request, 'pages/add_account.html')

def check_iban_format(iban):
    import re
    pattern = r'^FI\d{16}$'
    return re.match(pattern, iban) is not None

def loginView(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # FAULT 4: Cryptographic failure - Function uses a weak and insecure hashing algorithm for user authentication.
        user = authenticate_user(username=username, password=password)

        # FIX 4: Use Django's built-in password hashing for authentication instead of the custom hash_password function. This ensures that passwords are securely hashed and verified.
        # FIX 2: Use Django's built-in authentication system for user authentication
        # user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home')

        return render(request, 'pages/login.html', {'error': 'ERROR: Invalid username or password.'})

    return render(request, 'pages/login.html')


def logoutView(request):
    auth_logout(request)
    return redirect('login')


def registerView(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # FAULT 4: Cryptographic failure - The following code uses a weak and insecure hashing algorithm (Caesar cipher) to hash passwords, which can be easily reversed and does not provide adequate security for storing sensitive information like passwords.
        password = hash_password(password)
        if username and password:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO auth_user (username, password, is_staff, is_superuser, is_active, first_name, last_name, email, date_joined) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, '')",
                    [username, password, False, False, True, '', '', '']
                )

        # FIX 4: Use Django's built-in user creation method to securely create a new user with hashed password
        # if username and password:
        #     from django.contrib.auth.models import User
        #     User.objects.create_user(username=username, password=password)

        return redirect('login')
    return render(request, 'pages/register.html')



def deleteAccountView(request, account_id):
    if not request.user.is_authenticated:
        return redirect('login')


    try:
        # FAULT 3: Broken Access Control - The following code does not properly check if the account being deleted belongs to the authenticated user, allowing any authenticated user to delete any account by manipulating the URL.
        account = Account.objects.get(id=account_id)

        # FIX 3: Check if the account belongs to the user before deleting
        # account = Account.objects.get(id=account_id, owner=request.user)

        account.delete()

    except Account.DoesNotExist:
        accounts = Account.objects.filter(owner=request.user).order_by('iban')
        return render(request, 'pages/index.html', {'error': 'ERROR: Account not found or does not belong to you.', 'accounts': accounts})


    return redirect('home')


def homeView(request):
    if not request.user.is_authenticated:
        return redirect('login')

    accounts = Account.objects.filter(owner=request.user).order_by('iban')
    return render(request, 'pages/index.html', {'accounts': accounts})


def transferView(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        sender = request.POST.get('sender', '').strip()
        receiver = request.POST.get('receiver', '').strip()
        amount_value = request.POST.get('amount', '0')

        try:
            amount = int(amount_value)
        except (TypeError, ValueError):
            amount = 0

        result = transfer_accounts(sender, receiver, amount)
        if not result:
            accounts = Account.objects.filter(owner=request.user).order_by('iban')
            return render(request, 'pages/index.html', {'error': 'ERROR: Transfer failed. Please check the details and try again.' , 'accounts': accounts})

    return redirect('home')


def transfer_accounts(sender, receiver, amount):
    if amount < 0 or sender == receiver:
        return False

    try:
        with transaction.atomic():
            acc1 = Account.objects.get(iban=sender)
            acc2 = Account.objects.get(iban=receiver)
    except Account.DoesNotExist:
        return False

    if acc1.balance < amount:
        return False

    acc1.balance -= amount
    acc2.balance += amount

    acc1.save()
    acc2.save()
    return True
