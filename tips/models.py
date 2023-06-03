import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.validators import MinLengthValidator


def cafe_upload_path(instance, filename):
    return f"cafe_{instance.slug}/{filename}"

class Cafe(models.Model):
    slug = models.CharField(max_length=20, unique=True, default=uuid.uuid4().hex[:16])
    title = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    avatar = models.ImageField(upload_to=cafe_upload_path, blank=True)

    def __str__(self):
        return f"Cafe @{self.slug} {self.title}, location: {self.location}"


def user_upload_path(instance, filename):
    return f"user_{instance.username}/{filename}"

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=20, unique=True, default=uuid.uuid4().hex[:16])
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    email = models.CharField(max_length=50)
    avatar = models.ImageField(upload_to=user_upload_path, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # a admin user; non super-user
    is_superuser = models.BooleanField(default=False)  # a superuser
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"User @{self.username}, {self.first_name} {self.last_name}, email: {self.email}"


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    customer_wallet = models.CharField(max_length=42, validators=[MinLengthValidator(42)])

    def __str__(self):
        return f"Customer {self.user.username}, wallet: {self.customer_wallet}"


# automatically add Customer role to User
@receiver(post_save, sender=User)
def create_customer(sender, instance, created, **kwargs):
    if created:
        customer = Customer(user=instance)
        customer.save()


class Waiter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    waiter_wallet = models.CharField(max_length=42, blank=True, validators=[MinLengthValidator(42)])
    cafe = models.ForeignKey(Cafe, on_delete=models.CASCADE)

    def __str__(self):
        return f"Waiter {self.user.username} in cafe {self.cafe.title}, wallet: {self.waiter_wallet}"


# automatically fill in customer account for waiter
@receiver(pre_save, sender=Waiter)
def create_waiter_account(sender, instance, **kwargs):
    if instance.waiter_wallet == "" or instance.waiter_wallet is None:
        instance.waiter_wallet = instance.user.customer.customer_wallet


class CafeAdmin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cafe = models.ForeignKey(Cafe, on_delete=models.CASCADE)

    def __str__(self):
        return f"Cafe admin {self.user.username} in cafe {self.cafe.title}"


class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)  # TODO: do not delete transactions
    waiter = models.ForeignKey(Waiter, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now=True)
    amount = models.PositiveBigIntegerField()
    comment = models.CharField(max_length=200)

    def __str__(self):
        return (f"Transaction {self.id} from customer {self.customer} to waiter {self.waiter},"
                f"datetime: {self.datetime}, amount: {self.amount}, comment: {self.comment}")
