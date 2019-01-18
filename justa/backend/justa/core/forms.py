from functools import lru_cache
from hashlib import md5

from django.conf import settings
from django.forms import CharField, Form, ModelForm, ValidationError

from justa.core.models import CourtOrder


class TokenField(CharField):

    @property
    @lru_cache(maxsize=1)
    def token(self):
        return md5(settings.SECRET_KEY.encode()).hexdigest()

    def validate(self, value):
        if value != self.token:
            raise ValidationError("Token inválido")


class AuthenticationForm(Form):
    token = TokenField()


class CourtOrderForm(ModelForm):
    class Meta:
        model = CourtOrder
        fields = tuple(field.name for field in CourtOrder._meta.fields)
