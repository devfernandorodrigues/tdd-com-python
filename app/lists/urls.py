from django.urls import path
from lists import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('new', views.new_list, name='new_list'),
    path('<int:list_id>/', views.view_list, name='view_list'),
    path('<int:list_id>/add_item', views.add_item, name='add_item'),
]
