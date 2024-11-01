import random, hashlib
from string import digits

from django.core.cache import cache
from django.core.mail import send_mail

from config import settings
from apps.accounts.models import CustomUser


def generate_otp(user: CustomUser) -> str:
    if not isinstance(user, CustomUser):
        raise TypeError(f"{user} must be a CustomUser instance")

    user_string = (
        f"{user.email} + {user.username} + {user.first_name} + {user.last_name}"
    )
    otp_hash = hashlib.sha3_256(bytes(user_string, encoding="utf-8")).hexdigest()

    # check if an otp exists in the cache, and return it.
    if cache.has_key(otp_hash):
        return cache.get(otp_hash)

    otp = "".join(random.sample(digits, 6))

    try:
        cache.add(otp_hash, otp, timeout=60 * 15)
    except Exception as e:
        print(e)

    return otp


def otp_exists(user: CustomUser, otp: str) -> bool:
    if not isinstance(user, CustomUser):
        raise TypeError(f"{user} must be a CustomUser instance")

    user_string = (
        f"{user.email} + {user.username} + {user.first_name} + {user.last_name}"
    )
    cached_otp = cache.get(user_string)

    if cached_otp is not None and cached_otp == otp:
        cache.delete(user_string)
        return True
    else:
        return False


def send_otp_mail(otp: str, email: str) -> str:
    try:
        send_mail(
            "OTP mail from Blogr",
            f"Here is your OTP from Blogr: {otp}",
            settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )
        return "sent"
    except Exception as e:
        print(e)
        return "error"
