from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile, Teacher, Parent
# Department removed
from students.models import Student
import json

def register(request):
    """User registration view"""
    if request.method == 'POST':
        try:
            # Create user
            user = User.objects.create_user(
                username=request.POST.get('username'),
                email=request.POST.get('email'),
                password=request.POST.get('password'),
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name')
            )
            
            # Create user profile
            profile = UserProfile.objects.create(
                user=user,
                role=request.POST.get('role', 'student'),
                phone=request.POST.get('phone', ''),
                address=request.POST.get('address', ''),
                date_of_birth=request.POST.get('date_of_birth') or None
            )
            
            # Create role-specific profile
            role = request.POST.get('role')
            if role == 'teacher':
                Teacher.objects.create(
                    user=user,
                    employee_id=f"T{user.id:04d}",
                    designation=request.POST.get('designation', 'Teacher'),
                    hire_date=request.POST.get('hire_date') or '2024-01-01'
                )
            elif role == 'student':
                # Student profile will be created when application is approved
                pass
            elif role == 'parent':
                Parent.objects.create(
                    user=user,
                    relationship=request.POST.get('relationship', 'guardian'),
                    phone=request.POST.get('phone', ''),
                    occupation=request.POST.get('occupation', ''),
                    employer=request.POST.get('employer', ''),
                    address=request.POST.get('address', ''),
                    city=request.POST.get('city', ''),
                    state=request.POST.get('state', ''),
                    postal_code=request.POST.get('postal_code', ''),
                    country=request.POST.get('country', '')
                )
            
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('accounts:login')
            
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
    
    context = {
        'title': 'Register',
    }
    
    return render(request, 'accounts/register.html', context)

@login_required
def profile(request):
    """User profile view"""
    user = request.user
    
    context = {
        'title': 'Profile',
        'user': user,
    }
    
    # Add role-specific data
    try:
        if hasattr(user, 'profile'):
            context['user_profile'] = user.profile
            
            if user.profile.role == 'teacher' and hasattr(user, 'teacher_profile'):
                context['teacher_profile'] = user.teacher_profile
            elif user.profile.role == 'student' and hasattr(user, 'student_profile'):
                context['student_profile'] = user.student_profile
            elif user.profile.role == 'parent' and hasattr(user, 'parent_profile'):
                context['parent_profile'] = user.parent_profile
    except:
        pass
    
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile(request):
    """Edit user profile view"""
    user = request.user
    
    if request.method == 'POST':
        try:
            # Update user basic info
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.email = request.POST.get('email', user.email)
            user.save()
            
            # Update profile
            if hasattr(user, 'profile'):
                profile = user.profile
                profile.phone = request.POST.get('phone', profile.phone)
                profile.address = request.POST.get('address', profile.address)
                profile.bio = request.POST.get('bio', profile.bio)
                profile.website = request.POST.get('website', profile.website)
                profile.save()
            
            # Update role-specific profiles
            if user.profile.role == 'teacher' and hasattr(user, 'teacher_profile'):
                teacher = user.teacher_profile
                teacher.designation = request.POST.get('designation', teacher.designation)
                teacher.specialization = request.POST.get('specialization', teacher.specialization)
                teacher.office_room = request.POST.get('office_room', teacher.office_room)
                teacher.office_hours = request.POST.get('office_hours', teacher.office_hours)
                teacher.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
            
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
    
    context = {
        'title': 'Edit Profile',
        'user': user,
    }
    
    # Add role-specific data
    try:
        if hasattr(user, 'profile'):
            context['user_profile'] = user.profile
            
            if user.profile.role == 'teacher' and hasattr(user, 'teacher_profile'):
                context['teacher_profile'] = user.teacher_profile
            elif user.profile.role == 'student' and hasattr(user, 'student_profile'):
                context['student_profile'] = user.student_profile
            elif user.profile.role == 'parent' and hasattr(user, 'parent_profile'):
                context['parent_profile'] = user.parent_profile
    except:
        pass
    
    return render(request, 'accounts/edit_profile.html', context)