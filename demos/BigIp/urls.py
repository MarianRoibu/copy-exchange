from django.urls import path
from . import views

urlpatterns = [
    path('bigip', views.test_view, name='bigip'),

]