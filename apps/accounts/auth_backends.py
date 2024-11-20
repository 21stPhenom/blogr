import jwt
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.plumbing import build_bearer_security_scheme_object


from apps.accounts.models import CustomUser
from config.settings import SECRET_KEY


class JWTAuthentication(BaseAuthentication):
    """
    Backend for authenticating with JSON Web Tokens (JWT)
    """

    model = CustomUser
    keyword = "Bearer"

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        # ensure that only two values are contained in the authorization header
        if len(auth) == 1:
            msg = "Invalid authorization header. No credentials provided"
            raise AuthenticationFailed(msg)

        elif len(auth) > 2:
            msg = "Invalid token header. Token must not contain spaces."
            raise AuthenticationFailed(msg)

        # decode token
        try:
            token = auth[1].decode()
            user_data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.exceptions.InvalidSignatureError:
            msg = "Invalid token signature"
            raise AuthenticationFailed(msg)

        email, username, _, _ = user_data.values()
        try:
            user = self.model.objects.get(email=email, username=username)
        except self.model.DoesNotExist:
            msg = "Invalid token"
            raise AuthenticationFailed(msg)

        return (user, None)


class JWTScheme(OpenApiAuthenticationExtension):
    target_class = JWTAuthentication
    name = "jwtAuth"
    match_subclasses = True
    priority = -1

    def get_security_definition(self, auto_schema):
        return build_bearer_security_scheme_object(
            header_name="Authorization", token_prefix=self.target.keyword
        )
