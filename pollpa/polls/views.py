from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseNotAllowed
from django.template import loader
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from datetime import datetime
from .models import Poll, QuestionOption, VoteFingerprint, Vote, VoteChoice

from .models import Profile


def index(request):
    polls = Poll.objects.all().order_by("-closes")
    return render(request, 'polls/index.html', {
        "polls": polls
    })


def poll(request, poll_id):
    poll_obj = get_object_or_404(Poll, id=poll_id)
    
    state = poll_obj.state(request)

    error = None

    # Check if this is a vote submission
    if request.method == "POST" and state == "vote":
        print(request.POST)
        post_keys = request.POST.keys()
        vote_ids = [int(key[5:]) for key in post_keys if key.startswith("vote-")]
        selections = [QuestionOption.objects.get(id=vote) for vote in vote_ids]

        # Verify selections belong to this poll
        for selection in selections:
            if selection.question.poll != poll_obj:
                return HttpResponseNotAllowed()

        # Push vote markers into database
        VoteFingerprint.objects.create(poll=poll_obj, user=request.user)
        vote = Vote.objects.create(poll=poll_obj, grade=Profile.from_user(request.user).grade)
        for selection in selections:
            VoteChoice.objects.create(vote=vote, question=selection.question, choice=selection)

        # Recalculate state
        state = poll_obj.state(request)

    responses = None
    if state == "results":
        responses = []
        for question in poll_obj.questions:
            q_response = {
                "title": question.text,
                "description": question.description,
                "graph": question.chart,
                "xlabel": "Responses",
                "ylabel": "Count",
                "data": [{"x": choice.text, "y": VoteChoice.objects.filter(question=question, choice=choice).count()} for choice in question.options]
                # TODO: make binary slider work
            }
            responses.append(q_response)

    return render(request, 'polls/poll.html', {
        "poll": poll_obj,
        "error": error,
        "state": state,
        "responses": responses,
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
    if request.method == "POST":
        try:
            username = request.POST.get('username', None)
            if not username.endswith("@andover.edu"):
                username = username + "@andover.edu"
            password = request.POST.get('password', None)
            grade = int(request.POST.get('grade', None))
            if grade > 2022 or grade < 2019:
                raise Exception()
            user = User.objects.create_user(username, username, password)
            Profile.objects.create(user=user, grade=grade)
            login(request, user)
            return redirect("index")
        except Exception as e:
            print(e)
            context["error"] = "Unable to create your account with the given information; please try again. Either your email is either registered, or you forgot to select a graduation year."
    return render(request, 'polls/register.html', context)

def reset(request):
    return render(request, 'polls/reset-password.html', {})

def account(request):
    return render(request, 'polls/account.html', {})

def suggest(request):
    return render(request, 'polls/suggest.html', {})
