from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('element_location/', views.ElementLocation.as_view(), name='element_location'),
    path('element_instance/', views.ElementInstance.as_view(), name='element_instance'),
]