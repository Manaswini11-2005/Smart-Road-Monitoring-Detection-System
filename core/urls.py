from django.urls import path
from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('live/', views.LiveView.as_view(), name='live'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('results/', views.ResultsListView.as_view(), name='results'),
    path('export_report/', views.export_report_pdf, name='export_report'),
    path('api/upload/', views.mobile_api_upload, name='mobile_api'),
    path('video_upload/', views.video_upload, name='video_upload'),
]
