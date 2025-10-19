from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def role_test(request):
    """Simple role test view"""
    user = request.user
    
    # Get user role
    role = 'student'  # Default role
    try:
        user_profile = user.profile
        role = user_profile.role
    except Exception as e:
        if user.is_superuser:
            role = 'admin'
    
    context = {
        'username': user.username,
        'is_superuser': user.is_superuser,
        'is_staff': user.is_staff,
        'role': role,
        'profile_exists': hasattr(user, 'profile'),
        'profile_role': user.profile.role if hasattr(user, 'profile') else 'No profile',
    }
    
    return render(request, 'core/role_test.html', context)