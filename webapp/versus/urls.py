from django.urls import path
from . import views

app_name = 'versus'  # URL namespace

urlpatterns = [
    path('', views.VerseListView.as_view(), name='list'),
    path('create/', views.VerseCreateView.as_view(), name='create'),
    path('<int:pk>/', views.VerseDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.VerseEditView.as_view(), name='edit'),
] 