from django.urls import path, include
from lists import views as list_views
from lists import api_urls

urlpatterns = [
    path('', list_views.home_page, name='home'),
    path('lists/', include('lists.urls')),
    path('accounts/', include('accounts.urls')),
    path('api/', include(api_urls))
]
