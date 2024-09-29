from django.db import models
from app.users.models import User
from shortuuid.django_fields import ShortUUIDField
# Create your models here.

CATEGORY_CHOICE = (
    ("nap_vnd", "Nạp VNĐ"),
    ("rut_vnd", "Rút VND"),
    ("nap_usdt", "Nạp USDT"),
    ("rut_usdt", "Rút USDT")
)

STATUS = (
    ("fail", "Fail"),
    ("success", "Success"),
    ("waiting", "Waiting"),
)

class History(models.Model):
    code_id = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefgh12345", primary_key=True)
    payment =  models.DecimalField(decimal_places=2, max_digits=30, default=2)
    category = models.CharField(choices=CATEGORY_CHOICE, max_length=50, default="nap_vnd")
    status = models.CharField(choices=STATUS, max_length=50, default="waiting")
    time_create = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, related_name='user')