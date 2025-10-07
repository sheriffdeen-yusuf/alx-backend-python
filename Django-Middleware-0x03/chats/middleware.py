import os
import time
from datetime import datetime
from collections import defaultdict, deque
from django.http import HttpResponseForbidden


class RolepermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            # Accept if user is admin or moderator
            if hasattr(user, 'role'):
                if user.role in ['admin', 'moderator']:
                    return self.get_response(request)
                return HttpResponseForbidden('You do not have permission to perform this action.')
        return self.get_response(request)


class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Store timestamps of POSTs per IP
        self.ip_message_times = defaultdict(deque)

    def __call__(self, request):
        # Only limit POST requests to the message endpoint
        if request.method == 'POST' and '/messages' in request.path:
            ip = self.get_client_ip(request)
            now = time.time()
            window = 60  # 1 minute
            max_messages = 5
            times = self.ip_message_times[ip]
            # Remove timestamps older than 1 minute
            while times and now - times[0] > window:
                times.popleft()
            if len(times) >= max_messages:
                return HttpResponseForbidden(
                    'Message rate limit exceeded: 5 messages per minute.'
                )
            times.append(now)
        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        now = datetime.now().time()
        start = now.replace(hour=18, minute=0, second=0, microsecond=0)
        end = now.replace(hour=21, minute=0, second=0, microsecond=0)
        # Allow only between 18:00 (6PM) and 21:00 (9PM)
        if not (start <= now <= end):
            return HttpResponseForbidden(
                "Access to the chat is only allowed between 6PM and 9PM."
            )
        return self.get_response(request)


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.log_file = os.path.join(
            os.path.dirname(__file__),
            '../requests.log'
        )

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else 'Anonymous'
        log_entry = f"{datetime.now()} - User: {user} - Path: {request.path}\n"
        with open(self.log_file, 'a') as f:
            f.write(log_entry)
        response = self.get_response(request)
        return response
