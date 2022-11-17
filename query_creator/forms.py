from django import forms

from .LR_15 import gen_input_regions,all_warhouses
from .models import DataOrder

regions_list = gen_input_regions()[0]
regions_list = [tuple([i, i]) for i in regions_list]

warehouse_list = all_warhouses()
# megagavnocode here, but it works and fast
warehouse_list = [element for tupl in warehouse_list for element in tupl]
warehouse_list = [tuple([i, i]) for i in warehouse_list]

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column


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


class MakeOrderForm(forms.Form):
    # user should tell us what he wants to order from other site
    urls_list = forms.URLField(widget=forms.Textarea, label='Urls list', max_length=4000)
    # cosmetic
    urls_list.widget.attrs.update({'class': 'form-control', 'rows': 5})

    urls_list.widget.attrs.update({'placeholder': 'Enter urls separated by semicolon (;)'})

    urls_list.label = ''


    # add crispy forms


class AccountForm(forms.Form):
    name = forms.CharField(label='Name', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(label='Phone', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.CharField(label='Email', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    # user should tell us what he wants to order from other site
    region = forms.ChoiceField(choices=regions_list, label='Region',
                               widget=forms.Select(attrs={'class': 'form-control'}))
    # cosmetic
    name.widget.attrs.update({'placeholder': 'Name'})
    phone.widget.attrs.update({'placeholder': 'Phone'})
    email.widget.attrs.update({'placeholder': 'Email'})
    region.widget.attrs.update({'placeholder': 'Region'})
    name.label = ''
    phone.label = ''
    email.label = ''
    region.label = ''
    name.required = False
    phone.required = False
    email.required = False
    region.required = False


class PricingForm(forms.Form):
    select_from = forms.ChoiceField(choices=regions_list, widget=forms.Select(attrs={'class': 'form-control'}))
    select_to = forms.ChoiceField(choices=warehouse_list, widget=forms.Select(attrs={'class': 'form-control'}))
    select_from.label = ''
    select_to.label = ''
    select_from.required = False
    select_to.required = False


class DeleteOrderForm(forms.Form):
    # button to delete order
    order_id = forms.ChoiceField(label="chose order id to delete", required=False,choices=[], widget=forms.Select(attrs={'class': 'form-control'}))


