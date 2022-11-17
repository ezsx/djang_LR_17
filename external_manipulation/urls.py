from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views #import this

urlpatterns = [
    path('query_creator/', include('query_creator.urls')),
    path('admin/', admin.site.urls),
    # path('accounts/', include('django.contrib.auth.urls')),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='password/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name="password/password_reset_confirm.html"),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='password/password_reset_complete.html'),
         name='password_reset_complete'),

]
# urlpatterns += [
#     path('accounts/', include('django.contrib.auth.urls')),
#
# ]