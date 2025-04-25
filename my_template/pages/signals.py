from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

@receiver(user_logged_in)
def set_user_role(sender, request, user, **kwargs):
    if user.groups.filter(name='Admin').exists():
        request.session['role'] = 'admin'
    elif user.groups.filter(name='Superuser').exists():
        request.session['role'] = 'superuser'
    elif user.groups.filter(name='User').exists():
        request.session['role'] = 'user'
    else:
        request.session['role'] = 'guest'
