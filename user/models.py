from django.db import models
from django.contrib.auth.models import AbstractUser
from uuid import uuid4
# Create your models here.


class Profile(AbstractUser):
    id = models.UUIDField(default=uuid4,primary_key=True,editable=False,unique=True)


    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email','first_name','last_name']