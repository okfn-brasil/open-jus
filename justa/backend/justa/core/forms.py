from functools import lru_cache
from hashlib import md5

from django.conf import settings
from django.forms import CharField, ModelForm, ValidationError

from justa.core.models import CourtOrder


class TokenField(CharField):

    @property
    @lru_cache(maxsize=1)
    def token(self):
        return md5(settings.SECRET_KEY.encode()).hexdigest()

    def validate(self, value):
        if value != self.token:
            raise ValidationError("Token inválido")


class CourtOrderForm(ModelForm):
    token = TokenField()

    class Meta:
        model = CourtOrder
        fields = ('source', 'number', 'name', 'date', 'body', 'text')
