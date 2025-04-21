from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('poems/', include('poems.urls')),  # Updated to reflect correct import path
    # Redirect root URL to poems list
    path('', RedirectView.as_view(url='/poems/', permanent=False)),
] 