from django.urls import path
from main.views import Login

urlpatterns = [
    path('', Login.as_view(), name='login'),
]
