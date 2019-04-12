from django.core.mail import send_mail, send_mass_mail
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from datetime import timedelta
from django.utils import timezone
from django.core.mail import get_connection, EmailMultiAlternatives
import sys
from .models import AuthToken
import copy

def send_mass_html_mail(datatuple, fail_silently=False, user=None, password=None, 
                        connection=None):
    """
    Given a datatuple of (subject, text_content, html_content, from_email,
    recipient_list), sends each message to each recipient list. Returns the
    number of emails sent.

    If from_email is None, the DEFAULT_FROM_EMAIL setting is used.
    If auth_user and auth_password are set, they're used to log in.
    If auth_user is None, the EMAIL_HOST_USER setting is used.
    If auth_password is None, the EMAIL_HOST_PASSWORD setting is used.

    FROM https://stackoverflow.com/questions/7583801/send-mass-emails-with-emailmultialternatives/10215091#10215091

    """
    connection = connection or get_connection(
        username=user, password=password, fail_silently=fail_silently)
    messages = []
    for subject, text, html, from_email, recipient in datatuple:
        message = EmailMultiAlternatives(subject, text, from_email, recipient)
        message.attach_alternative(html, 'text/html')
        messages.append(message)
    return connection.send_messages(messages)

# Template is just the name of the file excluding the extension. So `/polls/emails/welcome.html`
# is just `welcome`. Note that there must be both a text version and an HTML version available.


def send_email(subject, template, to, context, grade, include_token=True):
    if include_token:
        context["token"] = AuthToken.objects.create(username=to, identifier=get_random_string(
            32), expires=(timezone.now() + timedelta(days=10)), grade=grade)
    html_render = render_to_string("polls/emails/" + template + ".html", context=context)
    text_render = render_to_string("polls/emails/" + template + ".txt", context=context)
    try:
        send_mail(subject, text_render, "PollPA <noreply@pollpa.com>",
                  [to], html_message=html_render)
    except Exception as e:
        print(e)

def send_many_emails(subject, template, to_grade_tuple, context, include_token=True):
    emails = []
    for to, grade in to_grade_tuple:
        local_context = copy.deepcopy(context)
        if include_token:
            local_context["token"] = AuthToken.objects.create(username=to, identifier=get_random_string(
                32), expires=(timezone.now() + timedelta(days=10)), grade=grade)
        html_render = render_to_string("polls/emails/" + template + ".html", context=local_context)
        text_render = render_to_string("polls/emails/" + template + ".txt", context=local_context)
        try:
            emails.append((subject, text_render, html_render, "PollPA <noreply@pollpa.com>", [to]))
        except Exception as e:
            print(e)
    return send_mass_html_mail(emails)