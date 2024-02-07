from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import HttpResponse, redirect

class Auth(MiddlewareMixin):
    def process_request(self, request):
        if request.path_info == "/users/login/":
            return
        elif request.path_info == "/users/create/":
            return
        elif request.path_info == "/start/":
            return
        else:
            info = request.session.get("info")
            if info:
                return
            # return redirect('/start/')
        
