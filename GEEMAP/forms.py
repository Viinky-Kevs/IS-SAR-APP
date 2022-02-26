from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUser(UserCreationForm):
	
	class Meta:
		model = User
		fields = ['username', 'first_name', 'last_name', 'email', 'password1','password2']
		widgets = {
			'field' : forms.TextInput(attrs={'class':'myfield'})
		}

class PolygonForm(forms.Form):
	enter_polygon = forms.CharField(widget=forms.Textarea)
	

class PointForm(forms.Form):
	Latitud = forms.FloatField(max_value=200, min_value=-200)
	Longitud = forms.FloatField(max_value=200, min_value=-200)