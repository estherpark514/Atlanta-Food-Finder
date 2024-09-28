from django.urls import path
from . import views


urlpatterns = [
    path('submit_review/<str:restaurant_id>/', views.submit_review, name='submit_review'),
    path('detail/<str:restaurant_id>/', views.restaurant_detail, name='detail'),
]