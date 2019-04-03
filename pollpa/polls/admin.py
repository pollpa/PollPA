from django.contrib import admin
from .models import Poll, AuthToken, Profile, VoteFingerprint, Question, QuestionOption, Vote, VoteChoice, Suggestion

# Register your models here.
admin.site.register(Poll)
admin.site.register(AuthToken)
admin.site.register(Profile)
admin.site.register(Question)
admin.site.register(QuestionOption)
admin.site.register(VoteFingerprint)
admin.site.register(Vote)
admin.site.register(VoteChoice)
admin.site.register(Suggestion)