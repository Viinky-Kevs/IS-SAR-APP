from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUser(UserCreationForm):
	
	class Meta:
		model = User
		fields = ['username', 'first_name', 'last_name', 'email', 'password1','password2']
		widgets = {'field' : forms.TextInput(attrs={'class':'myfield'})}

class PolygonForm(forms.Form):
	enter_polygon = forms.CharField(widget=forms.Textarea)
	name_p = forms.CharField(max_length=50)

class Polygon2Form(forms.Form):
	first_lat = forms.FloatField(min_value=-200, max_value=200)
	first_long = forms.FloatField(min_value=-200, max_value=200)
	second_lat = forms.FloatField(min_value=-200, max_value=200)
	second_long = forms.FloatField(min_value=-200, max_value=200)
	third_lat = forms.FloatField(min_value=-200, max_value=200)
	third_long = forms.FloatField(min_value=-200, max_value=200)
	fourth_lat = forms.FloatField(min_value=-200, max_value=200)
	fourth_long = forms.FloatField(min_value=-200, max_value=200)
	name_p = forms.CharField(max_length=50)