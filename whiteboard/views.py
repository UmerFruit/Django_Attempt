from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
import json
import logging

from .models import Whiteboard, WhiteboardSession

logger = logging.getLogger(__name__)


def home(request):
    """Home page showing public whiteboards and user's own whiteboards."""
    public_whiteboards = Whiteboard.objects.filter(is_public=True)[:10]
    user_whiteboards = []
    
    if request.user.is_authenticated:
        user_whiteboards = Whiteboard.objects.filter(owner=request.user)[:10]
    
    context = {
        'public_whiteboards': public_whiteboards,
        'user_whiteboards': user_whiteboards,
    }
    return render(request, 'whiteboard/home.html', context)


def register(request):
    """User registration view."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('whiteboard:home')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})


@login_required
def create_whiteboard(request):
    """Create a new whiteboard."""
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        is_public = request.POST.get('is_public') == 'on'
        
        if not title:
            messages.error(request, 'Title is required.')
            return render(request, 'whiteboard/create.html')
        
        whiteboard = Whiteboard.objects.create(
            title=title,
            owner=request.user,
            is_public=is_public
        )
        
        messages.success(request, f'Whiteboard "{title}" created successfully!')
        return redirect('whiteboard:view', pk=whiteboard.pk)
    
    return render(request, 'whiteboard/create.html')


def view_whiteboard(request, pk):
    """View/edit a specific whiteboard."""
    whiteboard = get_object_or_404(Whiteboard, pk=pk)
    
    # Check permissions
    if not whiteboard.can_view(request.user):
        return HttpResponseForbidden("You don't have permission to view this whiteboard.")
    
    # Track session for authenticated users
    if request.user.is_authenticated:
        session, created = WhiteboardSession.objects.get_or_create(
            whiteboard=whiteboard,
            user=request.user,
            defaults={'started_at': timezone.now()}
        )
        if not created:
            # Update the session timestamp
            session.started_at = timezone.now()
            session.save()
    
    context = {
        'whiteboard': whiteboard,
        'can_edit': whiteboard.can_edit(request.user),
        'drawing_data': json.dumps(whiteboard.get_drawing_data()),
    }
    
    return render(request, 'whiteboard/view.html', context)


@require_POST
@login_required
def save_whiteboard(request, pk):
    """Save whiteboard drawing data via AJAX."""
    whiteboard = get_object_or_404(Whiteboard, pk=pk)
    
    # Check permissions
    if not whiteboard.can_edit(request.user):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        data = json.loads(request.body)
        
        # Validate and sanitize the data
        validated_data = validate_drawing_data(data)
        
        whiteboard.data = validated_data
        whiteboard.save()
        
        return JsonResponse({'success': True, 'message': 'Whiteboard saved successfully'})
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Error saving whiteboard {pk}: {str(e)}")
        return JsonResponse({'error': 'Failed to save whiteboard'}, status=500)


@login_required
def delete_whiteboard(request, pk):
    """Delete a whiteboard."""
    whiteboard = get_object_or_404(Whiteboard, pk=pk)
    
    # Check permissions
    if not whiteboard.can_edit(request.user):
        return HttpResponseForbidden("You don't have permission to delete this whiteboard.")
    
    if request.method == 'POST':
        title = whiteboard.title
        whiteboard.delete()
        messages.success(request, f'Whiteboard "{title}" deleted successfully!')
        return redirect('whiteboard:home')
    
    return render(request, 'whiteboard/delete.html', {'whiteboard': whiteboard})


@login_required
def admin_dashboard(request):
    """Admin dashboard with analytics."""
    if not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    # Get analytics data
    total_whiteboards = Whiteboard.objects.count()
    total_users = WhiteboardSession.objects.values('user').distinct().count()
    
    # Sessions per day for the last 7 days
    sessions_data = []
    labels = []
    
    for i in range(6, -1, -1):
        date = timezone.now().date() - timedelta(days=i)
        sessions_count = WhiteboardSession.objects.filter(
            started_at__date=date
        ).count()
        sessions_data.append(sessions_count)
        labels.append(date.strftime('%a'))
    
    context = {
        'total_whiteboards': total_whiteboards,
        'total_users': total_users,
        'sessions_data': sessions_data,
        'labels': labels,
    }
    
    return render(request, 'whiteboard/admin_dashboard.html', context)


def validate_drawing_data(data):
    """Validate and sanitize drawing data in Fabric.js format."""
    if not isinstance(data, dict):
        raise ValueError("Data must be a dictionary")
    
    validated = {
        'version': '5.3.0',
        'objects': []
    }
    
    # Validate version
    if 'version' in data and isinstance(data['version'], str):
        validated['version'] = data['version']
    
    # Validate objects array
    if 'objects' in data and isinstance(data['objects'], list):
        for obj in data['objects']:
            if isinstance(obj, dict):
                validated_obj = {}
                
                # Copy safe properties
                safe_props = ['type', 'left', 'top', 'width', 'height', 'angle', 'scaleX', 'scaleY', 
                             'fill', 'stroke', 'strokeWidth', 'opacity', 'visible', 'path', 'text',
                             'fontSize', 'fontFamily', 'fontWeight', 'fontStyle', 'textAlign',
                             'radius', 'x1', 'y1', 'x2', 'y2']
                
                for prop in safe_props:
                    if prop in obj:
                        value = obj[prop]
                        # Basic validation for numeric values
                        if prop in ['left', 'top', 'width', 'height', 'angle', 'scaleX', 'scaleY', 
                                  'strokeWidth', 'opacity', 'fontSize', 'radius', 'x1', 'y1', 'x2', 'y2']:
                            if isinstance(value, (int, float)):
                                validated_obj[prop] = float(value)
                        # String validation
                        elif prop in ['type', 'fill', 'stroke', 'text', 'fontFamily', 'fontWeight', 
                                    'fontStyle', 'textAlign']:
                            if isinstance(value, str):
                                validated_obj[prop] = value
                        # Boolean validation
                        elif prop in ['visible']:
                            if isinstance(value, bool):
                                validated_obj[prop] = value                        # Array validation (for path data)
                        elif prop == 'path' and isinstance(value, list):
                            validated_obj[prop] = value
                
                # Only add objects that have at least a type
                if 'type' in validated_obj:
                    validated['objects'].append(validated_obj)
    
    return validated
