from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('versus/', include('versus.urls')),
    # Redirect root URL to verses list
    path('', RedirectView.as_view(url='/versus/', permanent=False)),
] 