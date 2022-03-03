from django.contrib import auth
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.shortcuts import reverse

from accounts.models import Token

def send_login_email(request):
    email = request.POST.get('email')
    token = Token.objects.create(email=email)
    url = request.build_absolute_uri(
        reverse('login') + f'?token={token.uid}'
    )
    message_body = f'Use this link to log in:\n\n{url}'

    send_mail(
      'Your login link for Superlists',
      message_body,
      'tddcompython@gmail.com',
      [email]
    )

    messages.success(
        request,
        "Check your email, we've sent you a link you can use to log in."
    )

    return redirect('/')


def login(request):
    user = auth.authenticate(uid=request.GET.get('token'))
    if user:
        auth.login(request, user)
    return redirect('/')
