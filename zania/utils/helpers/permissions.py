from rest_framework import permissions
from django.conf import settings
from rest_framework import status
from utils.helpers import constants


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

