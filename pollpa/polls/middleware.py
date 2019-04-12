from .models import AuthToken
from django.contrib.auth import login
from django.shortcuts import redirect
from django.utils import timezone

class AuthTokenMiddleware():
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        token_id = None
        token = None
        if request.GET.get("token", None) != None:
            token_id = request.GET.get("token", None)
        if request.POST.get("token", None) != None:
            token_id = request.POST.get("token", None)
        if token_id != None:
            token = AuthToken.objects.filter(identifier=token_id).first()
        if token != None and (not request.user.is_authenticated) and timezone.now() < token.expires:
            user = token.get_user_and_activate()
            if user != None:
                login(request, user)
                return redirect(request.path, permanent=True)
        if token_id != None:
            return redirect(request.path, permanent=True) # strip all parameters
        return response
        