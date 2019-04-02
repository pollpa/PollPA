from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from datetime import datetime

class Poll(models.Model):
    id = models.AutoField(primary_key=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    available = models.DateTimeField(db_index=True)
    closes = models.DateTimeField(db_index=True)
    public = models.DateTimeField(db_index=True)
    title = models.TextField()
    description = models.TextField(blank=True)

    @property
    def questions(self):
        return Question.objects.filter(poll=self)

    @property
    def votes(self):
        return Vote.objects.filter(poll=self)

    @property
    def is_completed(self):
        return datetime.utcnow() > self.closes

    @property
    def is_public(self):
        return datetime.utcnow() > self.public

    @property
    def is_available(self):
        return datetime.utcnow() > self.available

class AuthToken(models.Model):
    username = models.TextField()
    identifier = models.TextField(unique=True)
    expires = models.DateTimeField()
    metadata = models.TextField(default="{}")
    single_use = models.BooleanField(default=True)

    def get_user_and_activate(self):
        if self.expires > datetime.utcnow():
            return None
        user = User.objects.get(username=self.username)
        if user == None:
            password = get_random_string()
            user = User.objects.create_user(self.username, email=self.username, password=password)
            # TODO: send signup email
        if self.single_use:
            self.delete()
        return user

""" Supplement model for custom user data. Think of it as a user's settings. """
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    grade = models.IntegerField()
    send_emails = models.BooleanField(default=True)

""" Indicates _whether_ a user has voted. Does not contain the vote
 itself. This allows votes to be truthfully and absolutely separated
 from individual users, rendering votes completely anonymous—even
 to someone with full access to the database.
""" 
class VoteFingerprint(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Question(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    text = models.TextField()
    description = models.TextField(blank=True)
    kind = models.CharField(max_length=2, choices=[("MS", "Multiple Select (Checkboxes)"), ("SS", "Single Select (Radio)")], default="SS")

    @property
    def options(self):
        return QuestionOption.objects.filter(question=self)

class QuestionOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField()
    description = models.TextField(blank=True)

class Vote(models.Model):
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    grade = models.IntegerField()

class VoteChoice(models.Model):
    vote = models.ForeignKey(Vote, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(QuestionOption, on_delete=models.CASCADE)