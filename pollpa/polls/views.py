from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

def index(request):
    return render(request, 'polls/index.html', {})

def poll(request, poll_id):
    return render(request, 'polls/poll.html', {
        "poll_id": poll_id,
        "completed": False,
        "questions": [{
            "title": "Question 1 (Checkbox)?",
            "description": "Testing",
            "type": "checkbox",
            "options": [{
                "title": "a",
                "description": "This is a description."
            },
            {
                "title": "b",
                "description": ""
            },
            {
                "title": "c",
                "description": ""
            }]
        },
        {
            "title": "Question 2 (Radio)?",
            "description": "Testing",
            "type": "radio",
            "options": [{
                "title": "a",
                "description": ""
            },
            {
                "title": "b",
                "description": "This is a description"
            },
            {
                "title": "c",
                "description": ""
            }]
        }]
    })

def login(request):
    return render(request, 'polls/auth.html', {
        "title": "Login",
        "action": "/login"
    })
