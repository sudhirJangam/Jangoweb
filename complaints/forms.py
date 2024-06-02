from django.forms import ModelForm
from .models import Complaints

class ComplaintForm(ModelForm):
    class Meta:
        model = Complaints
        exclude = ('cluster',)