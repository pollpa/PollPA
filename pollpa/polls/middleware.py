from .models import AuthToken
from django.contrib.auth import login

class AuthTokenMiddleware():
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        token_id = None
        if request.GET.get("token", None) != None:
            token_id = request.GET.get("token", None)
        if request.POST.get("token", None) != None:
            token_id = request.POST.get("token", None)
        token = AuthToken.objects.filter(identifier=token_id).first()
        if token != None:
            user = token.get_user_and_activate()
            if user != None:
                login(request, user)
        
        return response
        