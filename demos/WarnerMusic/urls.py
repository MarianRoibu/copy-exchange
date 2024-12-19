from django.urls import path
from . import views

urlpatterns = [
    path('warnermusic', views.warner_music, name='warnermusic'),

]