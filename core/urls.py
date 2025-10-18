from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('test/', views.test_view, name='test'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<uuid:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('api/currency/convert/', views.CurrencyConverterView.as_view(), name='currency_convert'),
    path('api/currency/rates/', views.currency_rates, name='currency_rates'),
]
