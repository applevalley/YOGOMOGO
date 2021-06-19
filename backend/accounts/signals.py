from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User,Profile
from django.conf import settings
from rest_framework.authtoken.models import Token

from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail  
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives


# 작성 순서 => __init.py__에 app config default 설정 => apps.py에 ready일 때 import signals 설정
# 이후 원하는 signal 함수를 이곳에 작성하면 된다.

# 계정 생성시 Token 생성
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

# 계정 생성시 프로필 생성
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):

    context = {
        'current_user': reset_password_token.user,
        'username': reset_password_token.user.username,
        'email': reset_password_token.user.email,
        'reset_password_url': "{}?token={}".format(
            instance.request.build_absolute_uri(reverse('password_reset:reset-password-confirm')),
            reset_password_token.key)
    }

    request_user = User.objects.get(username=context['username'])
    user_token = Token.objects.get(user_id=request_user.pk)

    email_html_message = render_to_string('accounts/user_reset_password.html', context)
    email_plaintext_message = render_to_string('accounts/user_reset_password.txt', context)

    msg = EmailMultiAlternatives(
        # title:
        f'{request_user.username}님의 비밀번호 재설정 메일입니다.',
        # message:
        f'다음의 주소를 통해 접속하셔서, 비밀번호를 초기화해주세요. {email_plaintext_message}?{str(user_token)}',
        # from:
        "TeamBoatAdmin203@gmail.com",
        # to:
        [reset_password_token.user.email]
    )

  
    msg.send()