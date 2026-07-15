# A Vulnerable web application for educational purposes

This is a vulnerable web application built with Django for educational purposes. It contains several deliberate security vulnerabilities that can be exploited to learn about web application security. The vulnerabilities are marked with comments in the code and the fixes are commented out. The flaws are from OWASP Top 10 https://owasp.org/Top10/2021/ except for the CSRF vulnerability which is a common vulnerability in web applications.

## Running the application
`python manage.py makemigrations`
`python manage.py migrate`
`python manage.py runserver`

## Default accounts
- Username: bob, Password: squarepants
- Username: alice, Password: redqueen
- Username: admin, Password: admin

## Vulnerabilities
- FAULT 1: SQL Injection
- FAULT 2: Authentication failure
- FAULT 3: Broken access control
- FAULT 4: Cryptographic failure
- FAULT 5: CSRF