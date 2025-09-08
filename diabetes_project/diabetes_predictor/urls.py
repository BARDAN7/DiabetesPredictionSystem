from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', auth_views.LoginView.as_view(), name='login'),  # root = login
    path('signup/', views.signup, name='signup'),  
    path('index/', views.index, name='index'),   # index will be shown after login
    path('predict/', views.predict, name='predict'),
    path('result/', views.result, name='result'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('history/', views.history, name='history'),
    path('delete/<int:id>/', views.delete_record, name='delete_record'),
]

