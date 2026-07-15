from django.urls import path


from .views import (
    addAccountView,
    deleteAccountView,
    registerView,
    homeView,
    loginView,
    logoutView,
    transferView,
)


urlpatterns = [
    path('', homeView, name='home'),
    path('login/', loginView, name='login'),
    path('logout/', logoutView, name='logout'),
    path('register/', registerView, name='register'),
    path('add-account/', addAccountView, name='add_account'),
    path('delete-account/<int:account_id>/', deleteAccountView, name='delete_account'),
    path('transfer/', transferView, name='transfer'),
]
