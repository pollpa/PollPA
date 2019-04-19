from django.contrib import admin
from django.contrib.auth.models import User
from .models import Poll, AuthToken, Profile, VoteFingerprint, Question, QuestionOption, Vote, VoteChoice, Suggestion, AuthorizedEmail
from .email import send_email, send_many_emails

# Register your models here.
admin.site.register(AuthToken)
admin.site.register(Profile)
admin.site.register(Question)
admin.site.register(QuestionOption)
admin.site.register(VoteFingerprint)
admin.site.register(Vote)
admin.site.register(VoteChoice)
admin.site.register(AuthorizedEmail)

def announce_polls(modeladmin, request, queryset):
    for poll in queryset:
        to_grade_tuple = []
        for profile in Profile.objects.filter(send_emails=True):
            to_grade_tuple.append((profile.user.email, profile.grade))
        send_many_emails(poll.title, "poll", to_grade_tuple, {"poll": poll})

announce_polls.short_description = "Announce selected polls via email"

def welcome_poll(modeladmin, request, queryset):
    user_emails = [user.email for user in User.objects.all().only("email")]
    for poll in queryset:
        to_grade_tuple = []
        for auth in AuthorizedEmail.objects.all():
            if auth.email not in user_emails:
                to_grade_tuple.append((auth.email, auth.grade))
        send_many_emails("(Non) Sibi Culture", "introduction", to_grade_tuple, {"poll": poll})

welcome_poll.short_description = "Welcome non-registered emails using selected poll (non sibi culture)"

class PollAdmin(admin.ModelAdmin):
    list_display = ["title", "available", "closes"]
    ordering = ["closes"]
    actions = [announce_polls, welcome_poll]

admin.site.register(Poll, PollAdmin)

class SuggestionAdmin(admin.ModelAdmin):
    list_display = ["user", "status"]
    ordering = ["status"]
    actions = []

admin.site.register(Suggestion, SuggestionAdmin)
