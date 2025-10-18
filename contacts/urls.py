from django.urls import path
from . import views

app_name = 'contacts'

urlpatterns = [
    path('', views.contact_list, name='contact_list'),
    path('add/', views.add_contact, name='add_contact'),
    path('<uuid:contact_id>/', views.contact_detail, name='contact_detail'),
    path('<uuid:contact_id>/edit/', views.edit_contact, name='edit_contact'),
    path('<uuid:contact_id>/delete/', views.delete_contact, name='delete_contact'),
    path('api/<uuid:contact_id>/', views.ContactAPI.as_view(), name='contact_api'),
]
