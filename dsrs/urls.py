from django.urls import path

from . import views

app_name = "dsrs"
urlpatterns = [
    path('import_dsrs/', views.import_dsrs, name='import_dsrs'),
    path('percentile/<int:value>/', views.percentile, name='percentile'),
]