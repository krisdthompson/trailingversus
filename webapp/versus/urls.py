from django.urls import path
from . import views

app_name = 'versus'  # URL namespace

urlpatterns = [
    path('', views.VerseListView.as_view(), name='list'),
    path('create/', views.VerseCreateView.as_view(), name='create'),
    path('<slug:slug>/', views.VerseDetailView.as_view(), name='detail'),
    path('<slug:slug>/edit/', views.VerseEditView.as_view(), name='edit'),
    path('api/verse/<int:verse_id>/pattern/', views.save_verse_pattern, name='save_verse_pattern'),
    path('api/verse/<int:verse_id>/line/<str:line_id>/', views.save_verse_line, name='save_verse_line'),
] 