from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)


class Customer(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    phone = models.CharField(max_length=250,blank=True,null=True)
    secret_key = models.CharField(max_length=16, blank=True, null=True)
    fcm_token = models.CharField(max_length=16, blank=True, null=True)
    created_at = models.DateTimeField(_('created_date'), auto_now_add=True, editable=False, blank=True, null=True) 

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    


class Message(models.Model):
    sender = models.ForeignKey('Customer', related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey('Customer', related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    room_unique = models.CharField(max_length=300,null=True,blank=True)

    def __str__(self):
        return f"{self.sender.email} -> {self.receiver.email}: {self.content} ---{self.room_unique}"


class MessageHistory(models.Model):
    message = models.ForeignKey('Message', related_name='message_sub', on_delete=models.CASCADE)
    created_by = models.ForeignKey('Customer', related_name='history_related_messages', on_delete=models.CASCADE,null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.content}"


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Item(models.Model):
    item_name = models.CharField(max_length=100)
    price = models.FloatField(default=0)
    on_discount = models.BooleanField(default=False)
    discount_price = models.FloatField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    stock = models.IntegerField(default=0)
    description = models.TextField()

    def __str__(self):
        return self.item_name