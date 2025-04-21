from django.urls import path
from . import views

app_name = 'poems'  # Add URL namespace

urlpatterns = [
    path('', views.PoemListView.as_view(), name='list'),
    path('create/', views.PoemCreateView.as_view(), name='create'),
    path('<int:pk>/', views.PoemDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.PoemEditView.as_view(), name='edit'),
] 