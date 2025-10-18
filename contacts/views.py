from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from .models import Contact
import json


@login_required
def contact_list(request):
    """List all contacts with filtering and search"""
    contacts = Contact.objects.filter(is_active=True)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        contacts = contacts.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(notes__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(contacts, 20)  # Show 20 contacts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'total_contacts': contacts.count(),
    }
    
    return render(request, 'contacts/contact_list.html', context)


@login_required
def add_contact(request):
    """Add a new contact"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        facebook_url = request.POST.get('facebook_url', '').strip()
        notes = request.POST.get('notes', '').strip()
        
        if not name:
            messages.error(request, 'Name is required.')
            return render(request, 'contacts/add_contact.html')
        
        try:
            contact = Contact.objects.create(
                name=name,
                email=email if email else None,
                phone=phone if phone else None,
                facebook_url=facebook_url if facebook_url else None,
                notes=notes if notes else None,
                created_by=request.user
            )
            
            messages.success(request, f'Contact "{contact.name}" added successfully!')
            return redirect('contacts:contact_list')
            
        except Exception as e:
            messages.error(request, f'Error adding contact: {str(e)}')
    
    return render(request, 'contacts/add_contact.html')


@login_required
def contact_detail(request, contact_id):
    """View contact details"""
    contact = get_object_or_404(Contact, id=contact_id, is_active=True)
    
    context = {
        'contact': contact,
    }
    
    return render(request, 'contacts/contact_detail.html', context)


@login_required
def edit_contact(request, contact_id):
    """Edit contact details"""
    contact = get_object_or_404(Contact, id=contact_id, is_active=True)
    
    if request.method == 'POST':
        contact.name = request.POST.get('name', '').strip()
        contact.email = request.POST.get('email', '').strip()
        contact.phone = request.POST.get('phone', '').strip()
        contact.facebook_url = request.POST.get('facebook_url', '').strip()
        contact.notes = request.POST.get('notes', '').strip()
        
        if not contact.name:
            messages.error(request, 'Name is required.')
            return render(request, 'contacts/edit_contact.html', {'contact': contact})
        
        try:
            contact.email = contact.email if contact.email else None
            contact.phone = contact.phone if contact.phone else None
            contact.facebook_url = contact.facebook_url if contact.facebook_url else None
            contact.notes = contact.notes if contact.notes else None
            
            contact.save()
            
            messages.success(request, f'Contact "{contact.name}" updated successfully!')
            return redirect('contacts:contact_detail', contact_id=contact.id)
            
        except Exception as e:
            messages.error(request, f'Error updating contact: {str(e)}')
    
    context = {
        'contact': contact,
    }
    
    return render(request, 'contacts/edit_contact.html', context)


@login_required
def delete_contact(request, contact_id):
    """Delete contact (soft delete)"""
    contact = get_object_or_404(Contact, id=contact_id, is_active=True)
    
    if request.method == 'POST':
        try:
            contact.is_active = False
            contact.save()
            
            messages.success(request, f'Contact "{contact.name}" deleted successfully!')
            return redirect('contacts:contact_list')
            
        except Exception as e:
            messages.error(request, f'Error deleting contact: {str(e)}')
    
    context = {
        'contact': contact,
    }
    
    return render(request, 'contacts/delete_contact.html', context)


@method_decorator(csrf_exempt, name='dispatch')
class ContactAPI(View):
    """API for contact operations"""
    
    def get(self, request, contact_id):
        """Get contact data"""
        try:
            contact = Contact.objects.get(id=contact_id, is_active=True)
            
            return JsonResponse({
                'id': str(contact.id),
                'name': contact.name,
                'email': contact.email or '',
                'phone': contact.phone or '',
                'facebook_url': contact.facebook_url or '',
                'notes': contact.notes or '',
                'created_at': contact.created_at.isoformat(),
            })
            
        except Contact.DoesNotExist:
            return JsonResponse({'error': 'Contact not found'}, status=404)
    
    def post(self, request, contact_id):
        """Update contact data"""
        try:
            contact = Contact.objects.get(id=contact_id, is_active=True)
            data = json.loads(request.body)
            
            # Update allowed fields
            if 'name' in data:
                contact.name = data['name']
            if 'email' in data:
                contact.email = data['email']
            if 'phone' in data:
                contact.phone = data['phone']
            if 'facebook_url' in data:
                contact.facebook_url = data['facebook_url']
            if 'notes' in data:
                contact.notes = data['notes']
            
            contact.save()
            
            return JsonResponse({'success': True})
            
        except Contact.DoesNotExist:
            return JsonResponse({'error': 'Contact not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)