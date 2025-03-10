from rest_framework import permissions
from django.conf import settings


'''
PERMISSION CLASS FOR ALL OUR APIS
'''

class ApiKeyPermission(permissions.BasePermission):

	'''
	To check if our API Token if present at every request or not.
	'''

	def has_permission(self, request, view):
		api_key = request.META.get('HTTP_X_API_KEY', "")
		if 'docs' in request.path and settings.DEBUG:
			return True
		
		if api_key and api_key == settings.WEB_API_KEY:
			return True
		else:
			return False

	# @property
	def message(self):
		response_dict = {}
		response_dict['status'] = 'error'
		response_dict['message'] = 'Invalid Key'
		return response_dict



import time, sys
from ulid import ULID
from loguru import logger


log_format = "<b><green>{time:MMMM D, YYYY > HH:mm:ss}</green>  | <cyan> {level} </cyan>| <magenta><u>{message}</u> </magenta>| <e>{extra}</e></b>"
log_filename = ("loguru/log_{time}.log")

logger.configure(
    handlers=[
        dict(sink= sys.stdout,format= log_format,backtrace=True, diagnose=True),
        dict(
            sink=log_filename,
            level="TRACE", #log level
            enqueue=True, # async logging
            serialize=True, # first converted to a JSON string before being sent to the sink.
            rotation="100 MB",# Rotate logs after 100mb
            retention="7 days",  # Keep logs for 7 days
            ),
        ]
)


def logging_middleware(get_response):
    def middleware(request):
        request.start_time = time.time()

        # Use session-based request ID for authenticated users
        if request.user.is_authenticated:
            request_id = request.session.get("request_id")

            if not request_id:
                # Generate a new ULID and store it in the session if not present
                request_id = str(ULID())
                request.session["request_id"] = request_id
        else:
            # Generate a new ULID for each request for anonymous users
            request_id = str(ULID())

        # Add context to all loggers for the duration of the request
        with logger.contextualize(request_id=request_id):
            query_params = dict(request.GET)  # Capture query parameters (if any)

            # Get the response from the view
            response = get_response(request)

            elapsed = time.time() - request.start_time

            # Log incoming request details
            logger.bind(
                request_id=request_id,
                method=request.method,
                path=request.path,
                request_user=getattr(request, 'user', 'Anonymous'),
                client_ip=request.META.get('REMOTE_ADDR', ''),
                headers=dict(request.headers),
                query_params=query_params if query_params else None
            ).info(
                "incoming {method} request to {path} | query: {query_params}",
                method=request.method,
                path=request.path,
                query_params=query_params if query_params else "No query params",
            )

            # Log outgoing response details
            logger.bind(
                status_code=response.status_code,
                response_size=len(response.content),
                elapsed=elapsed,
                request_id=request_id,
            ).info(
                f"Processed request '{request.method}' to '{request.path}' in {elapsed:.2f}s"
            )

            # Set the request ID in the response headers
            response["X-Request-ID"] = request_id

            return response

    return middleware
