from django.urls import path
from . import views

app_name = 'batches'

urlpatterns = [
    path('', views.batch_list, name='batch_list'),
    path('add/', views.add_batch, name='add_batch'),
    path('<uuid:batch_id>/', views.batch_detail, name='batch_detail'),
    path('<uuid:batch_id>/edit/', views.edit_batch, name='edit_batch'),
    path('<uuid:batch_id>/delete/', views.delete_batch, name='delete_batch'),
    path('<uuid:batch_id>/students/', views.batch_students, name='batch_students'),
    path('<uuid:batch_id>/schedule/', views.batch_schedule, name='batch_schedule'),
    path('<uuid:batch_id>/attendance/', views.batch_attendance, name='batch_attendance'),
    path('<uuid:batch_id>/grades/', views.batch_grades, name='batch_grades'),
    path('api/<uuid:batch_id>/', views.BatchAPIView.as_view(), name='batch_api'),
]
