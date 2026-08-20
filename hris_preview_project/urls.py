from django.urls import path
from preview import views

urlpatterns = [
    path('', views.upload_view, name='upload'),
    path('download-errors/', views.download_errors_view, name='download_errors'),
]
