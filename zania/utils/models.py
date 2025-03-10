from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

# Create your models here.
def validate_image_format(image):
    valid_mime_types = ['image/jpeg','image/jpg','image/png']
    mime_type = image.file.content_type
    if mime_type not in valid_mime_types:
        raise ValidationError('Unsupported image format. Only JPEG/JPG is allowed.')


class TimeMixin(models.Model):
	"""
	TimeStamped Model
	An abstract base class model that provides default
	``added_on`` and ``updated_on`` fields.
	"""
	added_on = models.DateTimeField(auto_now_add=True)
	updated_on = models.DateTimeField(auto_now=True)

	class Meta:
		abstract = True
	

class AuthMixin(models.Model):
	"""
	Auth Stamped Model
	An abstract base class model that provides default
	``added_by`` and ``updated_by`` fields.
	"""
	added_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="%(app_label)s_%(class)s_added_by")
	updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="%(app_label)s_%(class)s_updated_by")

	class Meta:
		abstract = True


class LowercaseCharField(models.CharField):
    """
    Override EmailField to convert emails to lowercase before saving.
    """
    def to_python(self, value):
        """
        Convert email to lowercase.
        """
        value = super(LowercaseCharField, self).to_python(value)
        # Value can be None so check that it's a string before lowercasing.
        if isinstance(value, str):
            return value.lower()
        return value
	


class SoftDeleteQuerySet(models.QuerySet):
	def soft_delete(self):
		return self.update(is_active=False)

		
class SoftDeleteManager(models.Manager):
	def get_queryset(self):
		return SoftDeleteQuerySet(self.model).filter(is_active=True)
	
	def soft_delete(self):
		return self.get_queryset().soft_delete()
	
class SoftDeleteMixin(models.Model):
	# NOTE : Ensure SoftDeleteMixin is inherited at the beginning so it 
	# overrides 'objects' effectively.
	is_active = models.BooleanField(default=True, blank=False)
	
	objects = SoftDeleteManager()  # This filters active objects
	all_objects = models.Manager()  # This retrieves all objects, including soft-deleted ones
	
	def soft_delete(self, user=None):
		"""Soft deleting the instance by setting is_active=False"""
		self.is_active = False
		self.updated_by=user
		self.save()
	
	class Meta:
		default_manager_name = 'all_objects'
		abstract = True