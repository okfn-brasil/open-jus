from restless.dj import DjangoResource
from restless.exceptions import BadRequest
from restless.preparers import FieldsPreparer

from justa.core.models import CourtOrder
from justa.core.forms import AuthenticationForm, CourtOrderForm


class CourtOrderResource(DjangoResource):
    preparer = FieldsPreparer(fields={
        f.name: f.name
        for f in CourtOrder._meta.fields
    })

    def is_authenticated(self):
        if self.endpoint in {'list', 'detail'}:
            return True

        form = AuthenticationForm(self.request.POST)
        return form.is_valid()

    def list(self):
        return CourtOrder.objects.all()

    def detail(self, pk):
        return CourtOrder.objects.get(id=pk)

    def create(self):
        form = CourtOrderForm(self.data)
        if not form.is_valid():
            raise BadRequest(form.errors)

        return form.save()
