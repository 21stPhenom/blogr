from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.
class CustomUser(AbstractUser):
    email = models.EmailField(_('email_address'), unique=True)
    bio = models.CharField(verbose_name="User bio", max_length=500)
    topics = ArrayField(models.CharField(verbose_name='Topic', max_length=50, default=str), default=list)
    followers = models.ManyToManyField('self', symmetrical=False, related_name="followed_by")
    following = models.ManyToManyField('self', symmetrical=False, related_name="follows")

    
    def __str__(self):
        return f'{self.username}'
