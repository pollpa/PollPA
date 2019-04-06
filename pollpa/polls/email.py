from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from datetime import timedelta
from django.utils import timezone
import sys
from .models import AuthToken

# Template is just the name of the file excluding the extension. So `/polls/emails/welcome.html`
# is just `welcome`. Note that there must be both a text version and an HTML version available.


def send_email(subject, template, to, context, grade, include_token=True):
    if include_token:
        context["token"] = AuthToken.objects.create(username=to, identifier=get_random_string(
            32), expires=(timezone.now() + timedelta(days=1)), grade=grade)
    html_render = render_to_string("polls/emails/" + template + ".html", context=context)
    text_render = render_to_string("polls/emails/" + template + ".txt", context=context)
    try:
        send_mail(subject, text_render, "noreply@pollpa.com",
                  [to], html_message=html_render)
    except Exception as e:
        print(e)
