from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.utils import timezone

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
    def fingerprints(self):
        return VoteFingerprint.objects.filter(poll=self)

    @property
    def is_completed(self):
        return timezone.now() > self.closes

    @property
    def is_public(self):
        return timezone.now() > self.public

    @property
    def is_available(self):
        return timezone.now() > self.available

    @property
    def is_closed(self):
        return timezone.now() > self.closes

    def state(self, request):
        # Make sure the poll is available _or_ the user is a superuser
        if not (self.available < timezone.now() or request.user.is_superuser):
            raise Http404()

        # Check whether the results are public
        if self.public < timezone.now():
            return "results"

        # All other states require authentication
        if not request.user.is_authenticated:
            return "authenticate"

        user_has_voted = VoteFingerprint.objects.filter(poll=self, user=request.user).count() > 0

        # Check whether voting is in progress and the user can vote
        if self.available < timezone.now() and not user_has_voted and self.closes > timezone.now():
            return "vote"

        # Check whether the poll is closed but the user has voted
        if user_has_voted:
            return "results"

        # Check whether the poll is closed but the user has not voted
        if not user_has_voted:
            return "wait"

        # All states should be covered
        raise Exception("unknown state")

    def time_left(self):
        return self.closes - timezone.now()

""" Supplement model for custom user data. Think of it as a user's settings. """
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    grade = models.IntegerField()
    send_emails = models.BooleanField(default=True)

    @staticmethod
    def from_user(user):
        return Profile.objects.get(user=user)

class Suggestion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()

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
    chart = models.CharField(max_length=20, choices=[("bar", "Bar Chart"), ("binary-slider", "Binary Slider"), ("pie", "Pie Chart")], default="bar")

    @property
    def options(self):
        return QuestionOption.objects.filter(question=self).order_by("sorting_key")

class QuestionOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField()
    description = models.TextField(blank=True)
    sorting_key = models.FloatField(default=0)

class Vote(models.Model):
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    grade = models.IntegerField()

class VoteChoice(models.Model):
    vote = models.ForeignKey(Vote, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(QuestionOption, on_delete=models.CASCADE)

class AuthToken(models.Model):
    username = models.TextField()
    identifier = models.TextField(unique=True)
    expires = models.DateTimeField()
    grade = models.IntegerField()
    single_use = models.BooleanField(default=True)

    def get_user_and_activate(self):
        if self.expires < timezone.now():
            return None
        users = User.objects.filter(username=self.username)
        if users.count() == 0:
            password = get_random_string()
            user = User.objects.create_user(self.username, email=self.username, password=password)
            Profile.objects.create(grade=self.grade, user=user)
            return user
            # TODO: send signup email
        if self.single_use:
            self.delete()
        return users[0]