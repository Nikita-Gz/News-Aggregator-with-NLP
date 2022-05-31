from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Source


# Create your forms here.

class NewUserForm(UserCreationForm):
	email = forms.EmailField(required=True)

	class Meta:
		model = User
		fields = ("username", "email", "password1", "password2")

	def save(self, commit=True):
		user = super(NewUserForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		if commit:
			user.save()
		return user


class SourceSelectionForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(SourceSelectionForm, self).__init__(*args, **kwargs)
		self.fields['sourceChoices'].label = "Select news sources:"

	sourceChoices = forms.ModelMultipleChoiceField(
		queryset=Source.objects.all(),
		widget  = forms.CheckboxSelectMultiple,
		required=False)
	labels  = {'title':'Chose news sources to recommed:'}

	

