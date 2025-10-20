from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
from datetime import datetime, timedelta
import pandas as pd
import json
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO

from .models import StudentPayment, PaymentTransaction, PaymentImport
from students.models import Student
from batches.models import Batch
from core.models import Currency

@login_required
def payment_dashboard(request):
    """Simple payment dashboard"""
    # Get payment records
    payments = StudentPayment.objects.filter(is_active=True).select_related(
        'student', 'student__user', 'batch', 'currency'
    ).order_by('-created_at')
    
    # Filter by batch
    batch_filter = request.GET.get('batch', '')
    if batch_filter:
        payments = payments.filter(batch_id=batch_filter)
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        payments = payments.filter(status=status_filter)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        payments = payments.filter(
            Q(student__user__first_name__icontains=search_query) |
            Q(student__user__last_name__icontains=search_query) |
            Q(student__student_id__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(payments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    total_payments = StudentPayment.objects.filter(is_active=True).count()
    completed_payments = StudentPayment.objects.filter(is_active=True, status='completed').count()
    partial_payments = StudentPayment.objects.filter(is_active=True, status='partial').count()
    pending_payments = StudentPayment.objects.filter(is_active=True, status='pending').count()
    
    # Get selected batch for display
    selected_batch = None
    if batch_filter:
        try:
            selected_batch = Batch.objects.get(id=batch_filter, is_active=True)
        except Batch.DoesNotExist:
            selected_batch = None
    
    context = {
        'title': 'Payment Dashboard',
        'page_obj': page_obj,
        'batches': Batch.objects.filter(is_active=True),
        'search_query': search_query,
        'batch_filter': batch_filter,
        'status_filter': status_filter,
        'selected_batch': selected_batch,
        'total_payments': total_payments,
        'completed_payments': completed_payments,
        'partial_payments': partial_payments,
        'pending_payments': pending_payments,
    }
    
    return render(request, 'fees/payment_dashboard.html', context)

@login_required
def batch_payment_overview(request, batch_id):
    """Batch payment overview"""
    batch = get_object_or_404(Batch, id=batch_id, is_active=True)
    
    # Get all payments for this batch
    payments = StudentPayment.objects.filter(
        batch=batch, 
        is_active=True
    ).select_related('student', 'student__user', 'currency').order_by('student__student_id')
    
    # Calculate batch statistics
    total_students = payments.count()
    completed_payments = payments.filter(status='completed').count()
    partial_payments = payments.filter(status='partial').count()
    pending_payments = payments.filter(status='pending').count()
    
    # Calculate total amounts
    total_amount = sum(payment.total_amount for payment in payments)
    total_paid = sum(payment.get_total_paid() for payment in payments)
    total_remaining = total_amount - total_paid
    
    context = {
        'title': f'Payment Overview - {batch.name}',
        'batch': batch,
        'payments': payments,
        'total_students': total_students,
        'completed_payments': completed_payments,
        'partial_payments': partial_payments,
        'pending_payments': pending_payments,
        'total_amount': total_amount,
        'total_paid': total_paid,
        'total_remaining': total_remaining,
        'completion_percentage': (total_paid / total_amount * 100) if total_amount > 0 else 0,
    }
    
    return render(request, 'fees/batch_payment_overview.html', context)

@login_required
def payment_detail(request, payment_id):
    """Detailed view of a student's payment"""
    payment = get_object_or_404(StudentPayment, id=payment_id, is_active=True)
    
    # Get transactions
    transactions = payment.transactions.all().order_by('-payment_date')
    
    context = {
        'title': f'Payment Details - {payment.student.user.get_full_name()}',
        'payment': payment,
        'transactions': transactions,
    }
    
    return render(request, 'fees/payment_detail.html', context)

@login_required
def edit_payment(request, payment_id):
    """Edit payment record"""
    payment = get_object_or_404(StudentPayment, id=payment_id, is_active=True)
    
    if request.method == 'POST':
        try:
            # Update payment details
            payment.total_amount = float(request.POST.get('total_amount'))
            payment.currency_id = request.POST.get('currency')
            payment.payment_method = request.POST.get('payment_method')
            payment.notes = request.POST.get('notes', '')
            payment.save()
            
            messages.success(request, f'Payment record for {payment.student.user.get_full_name()} updated successfully!')
            return redirect('fees:payment_detail', payment_id=payment.id)
            
        except ValueError:
            messages.error(request, 'Invalid payment amount.')
        except Exception as e:
            messages.error(request, f'Error updating payment: {str(e)}')
    
    # Get available currencies
    currencies = Currency.objects.all()
    
    context = {
        'title': f'Edit Payment - {payment.student.user.get_full_name()}',
        'payment': payment,
        'currencies': currencies,
    }
    
    return render(request, 'fees/edit_payment.html', context)

@login_required
def delete_payment(request, payment_id):
    """Delete payment record"""
    payment = get_object_or_404(StudentPayment, id=payment_id, is_active=True)
    
    if request.method == 'POST':
        try:
            student_name = payment.student.user.get_full_name()
            payment.is_active = False
            payment.save()
            
            # Also deactivate all related transactions
            payment.transactions.update(is_active=False)
            
            messages.success(request, f'Payment record for {student_name} deleted successfully!')
            return redirect('fees:payment_dashboard')
            
        except Exception as e:
            messages.error(request, f'Error deleting payment: {str(e)}')
            return redirect('fees:payment_detail', payment_id=payment.id)
    
    # If GET request, redirect to payment detail
    return redirect('fees:payment_detail', payment_id=payment.id)

@login_required
def add_payment_transaction(request, payment_id):
    """Add a payment transaction"""
    payment = get_object_or_404(StudentPayment, id=payment_id)
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        payment_method = request.POST.get('payment_method', 'cash')
        notes = request.POST.get('notes', '')
        
        try:
            amount = float(amount)
            if amount <= 0:
                messages.error(request, 'Payment amount must be greater than 0.')
                return redirect('fees:payment_detail', payment_id=payment.id)
            
            # Check if payment exceeds remaining amount
            remaining = payment.get_remaining_amount()
            # Use a small tolerance for floating point comparison
            tolerance = 0.01
            if amount > remaining + tolerance:
                messages.error(request, f'Payment amount cannot exceed remaining amount of {remaining:.2f}.')
                return redirect('fees:payment_detail', payment_id=payment.id)
            
            # Create transaction
            transaction = PaymentTransaction.objects.create(
                payment=payment,
                amount=amount,
                payment_method=payment_method,
                notes=notes,
                processed_by=request.user  # Use User directly, not profile
            )
            
            messages.success(request, f'Payment of {amount} recorded successfully!')
            
        except ValueError:
            messages.error(request, 'Invalid payment amount.')
        except Exception as e:
            messages.error(request, f'Error recording payment: {str(e)}')
    
    return redirect('fees:payment_detail', payment_id=payment.id)

@login_required
def excel_import(request):
    """Excel import for payments"""
    if request.method == 'POST':
        try:
            batch_id = request.POST.get('batch')
            excel_file = request.FILES.get('excel_file')
            
            if not batch_id or not excel_file:
                messages.error(request, 'Please select a batch and upload an Excel file.')
                return redirect('fees:payment_dashboard')
            
            batch = get_object_or_404(Batch, id=batch_id)
            
            # Read Excel file
            df = pd.read_excel(excel_file)
            
            # Validate required columns
            required_columns = ['Student ID', 'Total Amount']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                messages.error(request, f'Missing required columns: {", ".join(missing_columns)}')
                return redirect('fees:payment_dashboard')
            
            # Create import record
            import_record = PaymentImport.objects.create(
                batch=batch,
                file_name=excel_file.name,
                imported_by=request.user.profile if hasattr(request.user, 'profile') else None,
                total_rows=len(df),
                status='processing'
            )
            
            successful_imports = 0
            failed_imports = 0
            error_log = []
            
            # Process each row
            for index, row in df.iterrows():
                try:
                    student_id = str(row['Student ID']).strip()
                    total_amount = float(row['Total Amount'])
                    
                    # Get student
                    student = Student.objects.get(student_id=student_id, is_active=True)
                    
                    # Get currency
                    currency_id = row.get('Currency ID', 1)
                    currency = Currency.objects.get(id=currency_id)
                    
                    # Create or update payment
                    payment, created = StudentPayment.objects.get_or_create(
                        student=student,
                        batch=batch,
                        defaults={
                            'total_amount': total_amount,
                            'currency': currency,
                            'created_by': request.user.profile if hasattr(request.user, 'profile') else None,
                            'notes': f'Imported from {excel_file.name}'
                        }
                    )
                    
                    if not created:
                        # Update existing payment
                        payment.total_amount = total_amount
                        payment.currency = currency
                        payment.created_by = request.user.profile if hasattr(request.user, 'profile') else None
                        payment.notes = f'Imported from {excel_file.name}'
                        payment.save()
                    
                    successful_imports += 1
                    
                except Student.DoesNotExist:
                    error_log.append(f"Row {index + 2}: Student ID '{student_id}' not found")
                    failed_imports += 1
                except Exception as e:
                    error_log.append(f"Row {index + 2}: {str(e)}")
                    failed_imports += 1
            
            # Update import record
            import_record.successful_imports = successful_imports
            import_record.failed_imports = failed_imports
            import_record.status = 'completed' if failed_imports == 0 else 'completed'
            import_record.error_log = '\n'.join(error_log)
            import_record.save()
            
            if successful_imports > 0:
                messages.success(request, f'Successfully imported {successful_imports} payments for {batch.name}.')
            if failed_imports > 0:
                messages.warning(request, f'{failed_imports} payments failed to import. Check the error log.')
            
        except Exception as e:
            messages.error(request, f'Error importing Excel file: {str(e)}')
    
    return redirect('fees:payment_dashboard')

@login_required
def download_template(request):
    """Download Excel template for payment import"""
    # Create template data
    template_data = {
        'Student ID': ['STU-2025-0001', 'STU-2025-0002'],
        'Total Amount': [50000, 75000],
        'Currency ID': [2, 2],  # BDT
        'Notes': ['Payment for student', 'Payment for student']
    }
    
    df = pd.DataFrame(template_data)
    
    # Create response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=payment_template.xlsx'
    
    df.to_excel(response, index=False)
    return response

@login_required
def export_batch_payments(request):
    """Export batch payment data to Excel"""
    batch_id = request.GET.get('batch')
    
    if not batch_id:
        messages.error(request, 'Please select a batch to export.')
        return redirect('fees:payment_dashboard')
    
    try:
        batch = Batch.objects.get(id=batch_id, is_active=True)
        
        # Get all payments for this batch
        payments = StudentPayment.objects.filter(
            batch=batch, 
            is_active=True
        ).select_related('student', 'student__user', 'currency').order_by('student__student_id')
        
        if not payments.exists():
            messages.warning(request, f'No payment records found for {batch.name}.')
            return redirect('fees:payment_dashboard')
        
        # Prepare data for Excel
        excel_data = []
        
        for payment in payments:
            student = payment.student
            user = student.user
            
            # Get transactions ordered by date
            transactions = payment.transactions.filter(is_active=True).order_by('payment_date')
            
            # First installment
            first_transaction = transactions.first() if transactions.exists() else None
            first_amount = first_transaction.amount if first_transaction else 0
            first_date = first_transaction.payment_date.date() if first_transaction else None
            
            # Second installment
            second_transaction = transactions[1] if len(transactions) > 1 else None
            second_amount = second_transaction.amount if second_transaction else 0
            second_date = second_transaction.payment_date.date() if second_transaction else None
            
            # Calculate remaining installments
            remaining_amount = payment.get_remaining_amount()
            total_paid = payment.get_total_paid()
            
            excel_data.append({
                'Student ID': student.student_id,
                'Student Name': user.get_full_name(),
                'Email': user.email if user.email else '',
                'Phone': student.phone if student.phone else '',
                'Batch': batch.name,
                'Total Amount': float(payment.total_amount),
                'Currency': payment.currency.code,
                'Payment Method': payment.get_payment_method_display(),
                'Status': payment.get_status_display(),
                'First Installment Amount': float(first_amount),
                'First Installment Date': first_date.strftime('%Y-%m-%d') if first_date else '',
                'Second Installment Amount': float(second_amount),
                'Second Installment Date': second_date.strftime('%Y-%m-%d') if second_date else '',
                'Total Paid': float(total_paid),
                'Remaining Amount': float(remaining_amount),
                'Progress (%)': round(payment.get_completion_percentage(), 2),
                'Notes': payment.notes if payment.notes else '',
                'Created Date': payment.created_at.strftime('%Y-%m-%d'),
            })
        
        # Create DataFrame
        df = pd.DataFrame(excel_data)
        
        # Create response
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        filename = f'batch_payments_{batch.name.replace(" ", "_")}_{datetime.now().strftime("%Y%m%d")}.xlsx'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Write to Excel with formatting
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Batch Payments', index=False)
            
            # Get the workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Batch Payments']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # Add header formatting
            from openpyxl.styles import Font, PatternFill, Alignment
            
            header_font = Font(bold=True, color='FFFFFF')
            header_fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
            header_alignment = Alignment(horizontal='center', vertical='center')
            
            for cell in worksheet[1]:
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_alignment
        
        messages.success(request, f'Successfully exported {len(excel_data)} payment records for {batch.name}.')
        return response
        
    except Batch.DoesNotExist:
        messages.error(request, 'Selected batch not found.')
        return redirect('fees:payment_dashboard')
    except Exception as e:
        messages.error(request, f'Error exporting data: {str(e)}')
        return redirect('fees:payment_dashboard')

@method_decorator(csrf_exempt, name='dispatch')
class PaymentAPI(View):
    """API for payment operations"""
    
    def post(self, request):
        """Create payment transaction via API"""
        try:
            data = json.loads(request.body)
            
            payment_id = data.get('payment_id')
            amount = float(data.get('amount'))
            payment_method = data.get('payment_method', 'cash')
            notes = data.get('notes', '')
            
            payment = StudentPayment.objects.get(id=payment_id)
            
            # Check if payment exceeds remaining amount
            remaining = payment.get_remaining_amount()
            # Use a small tolerance for floating point comparison
            tolerance = 0.01
            if amount > remaining + tolerance:
                return JsonResponse({'error': f'Payment amount cannot exceed remaining amount of {remaining:.2f}'}, status=400)
            
            # Create transaction
            transaction = PaymentTransaction.objects.create(
                payment=payment,
                amount=amount,
                payment_method=payment_method,
                notes=notes,
                processed_by=request.user  # Use User directly, not profile
            )
            
            return JsonResponse({
                'success': True,
                'transaction_id': transaction.id,
                'receipt_number': transaction.receipt_number,
                'remaining_amount': payment.get_remaining_amount()
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@login_required
def generate_receipt_pdf(request, transaction_id):
    """Generate PDF receipt for a payment transaction"""
    transaction = get_object_or_404(PaymentTransaction, id=transaction_id)
    payment = transaction.payment
    student = payment.student
    
    # Create PDF buffer
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        alignment=TA_LEFT,
        textColor=colors.darkblue
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=6,
        alignment=TA_LEFT
    )
    
    # Build PDF content
    story = []
    
    # Company Header
    story.append(Paragraph("Shahriar's Medical Academy", title_style))
    story.append(Spacer(1, 12))
    
    # Add logo if available
    try:
        logo_path = '/Users/istemamahmed/Desktop/Student Management System/static/images/sma-logo.jpg'
        if os.path.exists(logo_path):
            logo = Image(logo_path, width=2*inch, height=1*inch)
            logo.hAlign = 'CENTER'
            story.append(logo)
            story.append(Spacer(1, 12))
    except:
        pass  # Logo is optional
    
    story.append(Paragraph("PAYMENT RECEIPT", heading_style))
    story.append(Spacer(1, 12))
    
    # Receipt details
    receipt_data = [
        ['Receipt Number:', transaction.receipt_number],
        ['Date:', transaction.payment_date.strftime('%B %d, %Y at %I:%M %p')],
        ['Student ID:', student.student_id],
        ['Student Name:', student.user.get_full_name()],
        ['Batch:', payment.batch.name],
        ['Phone:', student.phone if student.phone else 'N/A'],
        ['Address:', student.address if student.address else 'N/A'],
    ]
    
    # Payment details table
    payment_table = Table(receipt_data, colWidths=[2*inch, 4*inch])
    payment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(payment_table)
    story.append(Spacer(1, 20))
    
    # Payment summary
    story.append(Paragraph("PAYMENT SUMMARY", heading_style))
    
    payment_summary_data = [
        ['Description', 'Amount'],
        ['Total Course Fee', f"{payment.currency.code} {payment.total_amount:,.2f}"],
        ['Amount Paid Previously', f"{payment.currency.code} {payment.get_total_paid() - float(transaction.amount):,.2f}"],
        ['Current Payment', f"{payment.currency.code} {transaction.amount:,.2f}"],
        ['Total Paid', f"{payment.currency.code} {payment.get_total_paid():,.2f}"],
        ['Remaining Balance', f"{payment.currency.code} {payment.get_remaining_amount():,.2f}"],
    ]
    
    summary_table = Table(payment_summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 20))
    
    # Payment method and notes
    story.append(Paragraph(f"Payment Method: {transaction.get_payment_method_display()}", normal_style))
    if transaction.notes:
        story.append(Paragraph(f"Notes: {transaction.notes}", normal_style))
    
    story.append(Spacer(1, 30))
    
    # Footer
    story.append(Paragraph("Thank you for your payment!", normal_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Shahriar's Medical Academy", normal_style))
    story.append(Paragraph("Contact: info@shahriaracademy.com", normal_style))
    
    # Build PDF
    doc.build(story)
    
    # Get PDF content
    pdf_content = buffer.getvalue()
    buffer.close()
    
    # Create HTTP response
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{transaction.receipt_number}.pdf"'
    
    return response

@login_required
def generate_payment_summary_pdf(request, payment_id):
    """Generate PDF summary for a student's payment record"""
    payment = get_object_or_404(StudentPayment, id=payment_id)
    student = payment.student
    transactions = payment.transactions.all().order_by('payment_date')
    
    # Create PDF buffer
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    # Define styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        alignment=TA_LEFT,
        textColor=colors.darkblue
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=6,
        alignment=TA_LEFT
    )
    
    # Build PDF content
    story = []
    
    # Company Header
    story.append(Paragraph("Shahriar's Medical Academy", title_style))
    story.append(Spacer(1, 12))
    
    # Add logo if available
    try:
        logo_path = '/Users/istemamahmed/Desktop/Student Management System/static/images/sma-logo.jpg'
        if os.path.exists(logo_path):
            logo = Image(logo_path, width=2*inch, height=1*inch)
            logo.hAlign = 'CENTER'
            story.append(logo)
            story.append(Spacer(1, 12))
    except:
        pass  # Logo is optional
    
    story.append(Paragraph("PAYMENT SUMMARY REPORT", heading_style))
    story.append(Spacer(1, 12))
    
    # Student details
    student_data = [
        ['Student ID:', student.student_id],
        ['Student Name:', student.user.get_full_name()],
        ['Batch:', payment.batch.name],
        ['Phone:', student.phone if student.phone else 'N/A'],
        ['Address:', student.address if student.address else 'N/A'],
        ['Enrollment Date:', payment.student.enrollment_date.strftime('%B %d, %Y')],
    ]
    
    student_table = Table(student_data, colWidths=[2*inch, 4*inch])
    student_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(student_table)
    story.append(Spacer(1, 20))
    
    # Payment transactions table
    story.append(Paragraph("PAYMENT TRANSACTIONS", heading_style))
    
    transaction_data = [['Receipt #', 'Date', 'Amount', 'Method', 'Notes']]
    
    for transaction in transactions:
        transaction_data.append([
            transaction.receipt_number,
            transaction.payment_date.strftime('%B %d, %Y'),
            f"{payment.currency.code} {transaction.amount:,.2f}",
            transaction.get_payment_method_display(),
            transaction.notes[:30] + '...' if len(transaction.notes) > 30 else transaction.notes
        ])
    
    transaction_table = Table(transaction_data, colWidths=[1.2*inch, 1.2*inch, 1*inch, 1*inch, 1.6*inch])
    transaction_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(transaction_table)
    story.append(Spacer(1, 20))
    
    # Payment summary
    story.append(Paragraph("PAYMENT SUMMARY", heading_style))
    
    summary_data = [
        ['Total Course Fee', f"{payment.currency.code} {payment.total_amount:,.2f}"],
        ['Total Paid', f"{payment.currency.code} {payment.get_total_paid():,.2f}"],
        ['Remaining Balance', f"{payment.currency.code} {payment.get_remaining_amount():,.2f}"],
        ['Payment Progress', f"{payment.get_completion_percentage():.1f}%"],
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 30))
    
    # Footer
    story.append(Paragraph("Generated on: " + datetime.now().strftime('%B %d, %Y at %I:%M %p'), normal_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Shahriar's Medical Academy", normal_style))
    
    # Build PDF
    doc.build(story)
    
    # Get PDF content
    pdf_content = buffer.getvalue()
    buffer.close()
    
    # Create HTTP response
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="payment_summary_{student.student_id}.pdf"'
    
    return response