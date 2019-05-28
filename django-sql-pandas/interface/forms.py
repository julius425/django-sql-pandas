from django import forms
from .models import NodeModel, DataBaseModel
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class NodeModelForm(forms.ModelForm):

    class Meta:
        model = NodeModel
        fields = ['node_id', 'time_from', 'time_to']


class DataBaseModelForm(forms.ModelForm):

    class Meta:
        model = DataBaseModel
        fields = ['db_name', 'db_address', 'db_user', 'db_psswd', 'sql_name']


class SignUpForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')