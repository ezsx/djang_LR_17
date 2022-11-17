import datetime

import datetime as dt
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render

from .forms import MakeOrderForm, PricingForm, AccountForm, DeleteOrderForm

from django.contrib.auth.decorators import login_required

from django.contrib.auth.mixins import LoginRequiredMixin

from .models import DataUser, DataOrder, DataPrice


def index(request):
    # if request.method == 'POST':
    # create a form instance and populate it with data from the request:
    if request.method == 'POST':
        content = request.POST
        user = request.user

        make_order_form = MakeOrderForm(content)
        pricing_form = PricingForm(content)
        personal_account_form = AccountForm(content)
        delete_order = DeleteOrderForm(content)
        # add to pricing form choices

        user_data_to_show = None
        orders = None
        if user.is_authenticated and DataOrder.objects.filter(user=user).exists():
            orders = DataOrder.objects.filter(user=user)

        user_url_list = None
        pricing_data = request.POST.get('pricing_data')
        print('pricing_data', pricing_data)

        if user.is_authenticated:
            # if user is authenticated, we can get his more data to past in database

            # check if user has account data
            if DataUser.objects.filter(user=user).exists():
                # if yes, show it in new form
                user_data = DataUser.objects.get(user=user)

                user_name = user_data.user.first_name
                user_phone = user_data.phone
                user_email = user_data.user.email
                user_region = user_data.region

                user_data_to_show = [user_name, user_phone, user_email, user_region]
                # if user want to change his data, we should delete old data and create new
                # if personal_account_form.is_valid():
                #     DataUser.objects.filter(user=user).delete()
                #     user_data = DataUser(user=user, phone=personal_account_form.cleaned_data['phone'],
                #                          region=personal_account_form.cleaned_data['region'])
                #     user_data.save()
                # personal_account_form = AccountForm(initial={'name': user_name, 'phone': user_phone, 'email': user_email, 'region': user_region})

            else:
                # if no, chek if user has filled personal account form
                # if yes, save it in database
                if personal_account_form.is_valid():
                    user.first_name = personal_account_form.cleaned_data['name']
                    user.email = personal_account_form.cleaned_data['email']
                    user_phone = personal_account_form.cleaned_data['phone']
                    user_region = personal_account_form.cleaned_data['region']
                    DataUser.objects.create(user=user, phone=user_phone, region=user_region)

                    return redirect(request.path)
                    # blank personal account form

        # check if user logged in
        if user.is_authenticated:
            # chech whether user has filled make order form
            # or its fake request

            if make_order_form.is_valid() and make_order_form.cleaned_data['urls_list'] != '':
                urls_list = tuple(make_order_form.cleaned_data['urls_list'].split(';')[:-1])

                DataOrder.objects.create(user=user, urls_list=urls_list, date=dt.datetime.now(),
                                         status='in progress')
                return redirect(request.path)
            if pricing_form.is_valid():
                select_from = pricing_form['select_from'].value()
                select_to = pricing_form['select_to'].value()
                print('select_from', select_from)
                print('select_to', select_to)
                from random import randint
                price = randint(100, 1000)
                from .LR_15 import count_time_delivery_from_region_to_warehouse
                datetime = count_time_delivery_from_region_to_warehouse(select_from, select_to)

                pricing_data = {'price': price, 'datetime': datetime, 'select_from': select_from,
                                'select_to': select_to}
                # add data to POST


        return render(request, 'index.html',
                      {'make_order_form': MakeOrderForm().as_p(), 'pricing_form': pricing_form.as_p(),
                       'account_form': AccountForm().as_p(), 'user': user, 'orders': orders,
                       'urls_list': user_url_list,
                       'delete_order': DeleteOrderForm().as_p(), 'user_data_to_show': user_data_to_show,
                       'pricing_data': pricing_data})

        # if a GET (or any other method) we'll create a blank form
    else:
        user = request.user
        orders = None
        user_data_to_show = None
        if user.is_authenticated:
            if DataOrder.objects.filter(user=user).exists():
                orders = DataOrder.objects.filter(user=user)
            if DataUser.objects.filter(user=user).exists():
                user_data = DataUser.objects.get(user=user)
                user_name = user_data.user.first_name
                user_phone = user_data.phone
                user_email = user_data.user.email
                user_region = user_data.region

                user_data_to_show = [user_name, user_phone, user_email, user_region]

        return render(request, 'index.html',
                      {'make_order_form': MakeOrderForm().as_p(), 'pricing_form': PricingForm().as_p(),
                       'account_form': AccountForm().as_p(), 'user': user, 'orders': orders,
                       'delete_order': DeleteOrderForm().as_p(), 'user_data_to_show': user_data_to_show})


from django.shortcuts import render, redirect
from .forms import NewUserForm
from django.contrib.auth import login
from django.contrib import messages


def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("query_creator:index")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render(request=request, template_name="registration/register.html", context={"register_form": form})


from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("query_creator:index")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="registration/login.html", context={"login_form": form})


from django.contrib.auth import login, authenticate, logout


def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("query_creator:index")


from django.shortcuts import render, redirect
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.contrib import messages  # import messages


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "password/password_reset_email.txt"
                    c = {
                        "email": user.email,
                        'domain': '127.0.0.1:8000',
                        'site_name': 'Website',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, 'admin@example.com', [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    messages.success(request, 'A message with reset password instructions has been sent to your inbox.')

                    return redirect("query_creator:index")
                messages.error(request, 'An invalid email has been entered.')
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="password/password_reset.html",
                  context={"password_reset_form": password_reset_form})
