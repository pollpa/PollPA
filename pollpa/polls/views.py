from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseNotAllowed
from django.template import loader
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from .models import Poll, QuestionOption, VoteFingerprint, Vote, VoteChoice, Suggestion, AuthToken, AuthorizedEmail, Question
from .models import Profile
from django.db.models import Count
from .email import send_email
from django.contrib.auth.decorators import user_passes_test
import json
from django.utils import timezone

def index(request):
    polls = [poll for poll in Poll.objects.all().order_by("-closes")
             if poll.is_available]
    return render(request, 'polls/index.html', {
        "polls": polls,
        "most_recent_poll_id": polls[0].id
    })


def poll(request, poll_id):
    poll_obj = get_object_or_404(Poll, id=poll_id)

    state = poll_obj.state(request)

    validation = {
        "status": None,
        "text": None
    }

    filter_settings = {
        "grade": "all"
    }

    # Check if this is a vote submission
    if request.method == "POST":
        if state != "vote":
            validation["status"] = "error"
            validation["text"] = "You cannot vote in this poll at this time."
        else:
            def _question(id):
                return Question.objects.get(id=id)

            post_keys = request.POST.keys()

            question_choice_ids = []

            # Verify all questions are answered properly
            for question in poll_obj.questions:
                handle = "question-" + str(question.id)
                valid_choice_ids = [choice.id for choice in question.options]
                if handle in post_keys:
                    selections = request.POST.getlist(handle)
                    choices = [int(s[7:]) for s in selections]
                    if question.kind == "MS":
                        if len(choices) < 1:
                            validation["status"] = "error"
                            validation["text"] = "You must select at least one option for the question '%s'" % question.text
                        else:
                            for choice in choices:
                                if choice not in valid_choice_ids:
                                    return HttpResponseNotAllowed()
                                question_choice_ids.append(choice)
                    elif question.kind == "SS":
                        if len(choices) != 1:
                            validation["status"] = "error"
                            validation["text"] = "You must select exactly one option for the question '%s'" % question.text
                        else:
                            for choice in choices:
                                if choice not in valid_choice_ids:
                                    return HttpResponseNotAllowed()
                                question_choice_ids.append(choice)
                else:
                    validation["status"] = "error"
                    validation["text"] = "You must answer the question '%s'" % question.text

            if validation["status"] == None:
                # Push vote markers into database
                VoteFingerprint.objects.create(
                    poll=poll_obj, user=request.user)
                vote = Vote.objects.create(
                    poll=poll_obj, grade=Profile.from_user(request.user).grade)
                for choice_id in question_choice_ids:
                    choice = QuestionOption.objects.get(id=choice_id)
                    VoteChoice.objects.create(
                        vote=vote, question=choice.question, choice=choice)

                validation = {
                    "status": "success",
                    "text": "Your vote has been successfully recorded. You may now view the preliminary results."
                }

            # Recalculate state
            state = poll_obj.state(request)

    responses = None
    if state == "results":
        filter_class = request.GET.get("filter", "all")
        filter_settings["grade"] = filter_class
        vote_choices = VoteChoice.objects.filter(question__poll=poll_obj)
        if filter_class != "all":
            vote_choices = vote_choices.filter(vote__grade=int(filter_class))
            filter_settings["total"] = Vote.objects.filter(
                grade=int(filter_class), poll=poll_obj).count()
        else:
            filter_settings["total"] = Vote.objects.filter(
                poll=poll_obj).count()
        responses = []
        for question in poll_obj.questions:
            q_response = {
                "title": question.text,
                "description": question.description,
                "graph": question.chart,
                "xlabel": "Responses",
                "ylabel": "Count",
                "filter_settings": filter_settings,
                "data": [{"x": choice.text, "y": vote_choices.filter(question=question, choice=choice).count()} for choice in question.options]
            }
            responses.append(q_response)

    has_user_voted = False
    if request.user.is_authenticated:
        has_user_voted = VoteFingerprint.objects.filter(
            user=request.user, poll=poll_obj).count() > 0

    return render(request, 'polls/poll.html', {
        "poll": poll_obj,
        "error": None,
        "state": state,
        "responses": responses,
        "validation": validation,
        "grades": ["2022", "2021", "2020", "2019"],
        "filter_settings": filter_settings,
        "has_user_voted": has_user_voted
    })


def _logout(request):
    logout(request)
    return redirect("index")


def _login(request):
    context = {
        "error": None
    }
    if request.user.is_authenticated:
        return redirect("index")
    if request.method == "POST":
        # emails and usernames are _always_ the same
        username = request.POST.get('email', None)
        password = request.POST.get('password', None)
        if not username.endswith("@andover.edu"):
            username = username + "@andover.edu"
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            context["error"] = "Invalid username or password!"
    return render(request, 'polls/login.html', context)


def register(request):
    context = {
        "error": None
    }
    if request.user.is_authenticated:
        return redirect("index")
    if request.method == "POST":
        try:
            username = request.POST.get('username', None)
            if not username.endswith("@andover.edu"):
                username = username + "@andover.edu"
            username = username.lower()
            authorization = AuthorizedEmail.objects.get(email=username)
            password = request.POST.get('password', None)
            verify_password = request.POST.get('verify-password', None)
            if password != verify_password:
                raise Exception()
            grade = authorization.grade
            user = User.objects.create_user(username, username, password)
            Profile.objects.create(user=user, grade=grade)
            send_email("Your PollPA account has been created!",
                       "welcome", user.email, {"user": user}, Profile.from_user(user).grade)
            login(request, user)
            return redirect("index")
        except Exception as e:
            print(e)
            context["error"] = "Please try again. Either your email is already registered, your email is not a valid Phillips Academy email, or your passwords don't match."
    return render(request, 'polls/register.html', context)


def reset(request):
    maybe_sent_email = False
    if request.method == "POST":
        email = request.POST.get("email", None)
        if email is not None:
            maybe_sent_email = True
            email = email.lower()
            if not email.endswith("andover.edu"):
                email = email + "@andover.edu"
            try:
                user = User.objects.get(email=email)
                send_email("PollPA Password Reset Request", "reset",
                        email, context={}, grade=Profile.from_user(user).grade)
            except Exception as e:
                pass
    return render(request, 'polls/reset-password.html', {"maybe_sent_email": maybe_sent_email})


@login_required(login_url="/login")
def account(request):
    profile = Profile.from_user(request.user)

    submitted = False

    if request.method == "POST":
        password = request.POST.get("password", "")
        send_email = "emailupdates" in request.POST
        if send_email != profile.send_emails:
            profile.send_emails = send_email
            profile.save()
            submitted = True
        if len(password) != 0:
            request.user.set_password(password)
            request.user.save()
            submitted = True

    return render(request, 'polls/account.html', {
        "profile": profile,
        "submitted": submitted
    })


@login_required(login_url="/login")
def suggest(request):
    submitted = False
    if request.method == "POST":
        Suggestion.objects.create(
            user=request.user, text=request.POST.get("text")[:9999])
        submitted = True
    return render(request, 'polls/suggest.html', {
        "submitted": submitted
    })


def latest(request):
    latest = [poll for poll in Poll.objects.filter().order_by(
        "-closes") if poll.is_available][0].id
    return redirect("poll", poll_id=latest)


@login_required(login_url="/login")
def logout_everywhere(request):
    logout(request.user)
    AuthToken.objects.filter(user=request.user).delete()
    return redirect("index")

@user_passes_test(lambda u: u.is_superuser)
def management(request):

    submitted = False
    messages = []

    if request.method == "POST":
        poll_raw = request.POST.get("poll", "")
        emails = request.POST.get("emails", "")
        
        # Check if there is a question to import
        if len(poll_raw) > 0:
            poll_data = json.loads(poll_raw)
            time = timezone.now() + timedelta(days=365)
            poll = Poll.objects.create(title=poll_data.get("title"), description=poll_data.get("description"), about=poll_data.get("about"), available=time, closes=time, public=time)
            for question_obj in poll_data.get("questions"):
                question = Question.objects.create(poll=poll, text=question_obj.get("text"), description=question_obj.get("description", ""), kind=question_obj.get("kind"), chart=question_obj.get("chart"))
                i = 0
                for option_obj in question_obj.get("options"):
                    option = QuestionOption.objects.create(question=question, sorting_key=i, text=option_obj.get("text"), description=option_obj.get("description", ""))
                    i += 1
            submitted = True
            messages.append({
                "title": "Successfully imported question!",
                "description": "Be sure to input correct dates in the dashboard."
            })
        if len(emails) > 0:
            lines = emails.split("\n")
            for line in lines:
                email, graduation_year = line.replace(" ", "").split(",")
                AuthorizedEmail.objects.get_or_create(email=email, grade=int(graduation_year))
            submitted = True
            messages.append({
                "title": "Successfully imported %s users!" % (str(len(lines))),
                "description": "These users can now register."
            })
    print(messages)
    return render(request, 'polls/management.html', {
        "submitted": submitted,
        "messages": messages
    })