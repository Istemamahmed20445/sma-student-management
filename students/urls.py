from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('', views.student_list, name='student_list'),
    path('add/', views.add_student, name='add_student'),
    path('<str:student_id>/', views.student_detail, name='student_detail'),
    path('<str:student_id>/edit/', views.edit_student, name='edit_student'),
    path('<str:student_id>/delete/', views.delete_student, name='delete_student'),
    path('applications/', views.student_application_list, name='application_list'),
    path('applications/<uuid:application_id>/', views.student_application_detail, name='application_detail'),
    path('applications/<uuid:application_id>/update-status/', views.update_application_status, name='update_application_status'),
    path('apply/', views.student_application_form, name='application_form'),
    path('apply/success/<uuid:application_id>/', views.application_success, name='application_success'),
    path('api/check-duplicate/', views.check_duplicate_student, name='check_duplicate_student'),
    path('api/<str:student_id>/', views.StudentAPIView.as_view(), name='student_api'),
    path('not-found/', views.student_not_found, name='student_not_found'),
]
