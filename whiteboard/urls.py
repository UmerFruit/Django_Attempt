from django.urls import path
from . import views

app_name = 'whiteboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('create/', views.create_whiteboard, name='create'),
    path('whiteboard/<int:pk>/', views.view_whiteboard, name='view'),
    path('whiteboard/<int:pk>/save/', views.save_whiteboard, name='save'),
    path('whiteboard/<int:pk>/delete/', views.delete_whiteboard, name='delete'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
