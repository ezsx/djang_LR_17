from django.urls import path

from . import views

app_name = "query_creator"
urlpatterns = [
    # main page
    #    (about us, contact us, menu links etc.)
    path("", views.index, name='index'),
    path("register", views.register_request, name="register"),
    path("login", views.login_request, name="login"),
    path("logout", views.logout_request, name="logout"),
    path("password_reset", views.password_reset_request, name="password_reset")

]
