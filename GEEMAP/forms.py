from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

import pandas as pd
import os

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

file1 = pd.read_excel('./media/excel/user.xlsx')
file1 = pd.DataFrame(file1)

file2 = pd.read_excel('./media/excel/data.xlsx')
file2 = pd.DataFrame(file2)

current_user = file1['current_user'][0]

lotes_disponibles = [(0, 'txt_test_NOT')]
counter = 0
for i in range(len(file2)):
	if file2['name_user'][i] == current_user:
		if file2['name_polygon'][i] not in lotes_disponibles[counter][1]:
			counter += 1
			lotes_disponibles.append((file2['name_polygon'][i], file2['name_polygon'][i]))
		else:
			continue
	else:
		continue

lotes_disponibles.pop(0)

class SavePolygonForm(forms.Form):
	options = forms.ChoiceField(choices = lotes_disponibles)


parent_dir = './media/'
file3 = pd.read_excel('./media/excel/user.xlsx')
file3 = pd.DataFrame(file3)
user_name = file3['current_user'][0]
	
path = os.path.join(parent_dir, user_name)
directory_cont = os.listdir(path)

lista = []
for i in directory_cont:
    f = i.split('.')
    if f[1] == 'shp' or f[1] == 'kml':
        lista.append((i, i))

class ConfiUpForm(forms.Form):
	options = forms.ChoiceField(choices = lista)