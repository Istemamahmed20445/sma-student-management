from django.urls import path
from . import views

app_name = 'fees'

urlpatterns = [
    path('', views.payment_dashboard, name='payment_dashboard'),
    path('batch/<uuid:batch_id>/', views.batch_payment_overview, name='batch_payment_overview'),
    path('payment/<uuid:payment_id>/', views.payment_detail, name='payment_detail'),
    path('payment/<uuid:payment_id>/edit/', views.edit_payment, name='edit_payment'),
    path('payment/<uuid:payment_id>/delete/', views.delete_payment, name='delete_payment'),
    path('payment/<uuid:payment_id>/add-transaction/', views.add_payment_transaction, name='add_payment_transaction'),
    path('payment/<uuid:payment_id>/print-summary/', views.generate_payment_summary_pdf, name='print_payment_summary'),
    path('transaction/<uuid:transaction_id>/print-receipt/', views.generate_receipt_pdf, name='print_receipt'),
    path('excel-import/', views.excel_import, name='excel_import'),
    path('download-template/', views.download_template, name='download_template'),
    path('export-batch/', views.export_batch_payments, name='export_batch_payments'),
    path('api/payment/', views.PaymentAPI.as_view(), name='payment_api'),
]