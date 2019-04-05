from django.contrib import admin
from .models import Poll, AuthToken, Profile, VoteFingerprint, Question, QuestionOption, Vote, VoteChoice, Suggestion
from .email import send_email

# Register your models here.
admin.site.register(AuthToken)
admin.site.register(Profile)
admin.site.register(Question)
admin.site.register(QuestionOption)
admin.site.register(VoteFingerprint)
admin.site.register(Vote)
admin.site.register(VoteChoice)
admin.site.register(Suggestion)

def announce_polls(modeladmin, request, queryset):
    for poll in queryset:
        for profile in Profile.objects.filter(send_emails=True):
            send_email(poll.title, "poll", profile.user.email, {"poll": poll}, profile.grade)

announce_polls.short_description = "Announce selected polls via email"

class PollAdmin(admin.ModelAdmin):
    list_display = ["title", "available", "closes"]
    ordering = ["closes"]
    actions = [announce_polls]

admin.site.register(Poll, PollAdmin)