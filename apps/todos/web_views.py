"""Web-based views for Todo application with form handling and HTML rendering."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from .models import Todo
from .forms import SignupForm, LoginForm, TodoForm


# ============================================================================
# AUTHENTICATION VIEWS (Web Templates)
# ============================================================================

def index(request):
    """Homepage redirect to todos or login."""
    if request.user.is_authenticated:
        return redirect('todos:list')
    return render(request, 'index.html')


@require_http_methods(['GET', 'POST'])
def signup_view(request):
    """User registration page."""
    if request.user.is_authenticated:
        return redirect('todos:list')
    
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            # Create user with email as username
            user = User.objects.create_user(
                username=form.cleaned_data['email'],
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                password=form.cleaned_data['password'],
            )
            # Log user in
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome!')
            return redirect('todos:list')
    else:
        form = SignupForm()
    
    return render(request, 'auth/signup.html', {'form': form})


@require_http_methods(['GET', 'POST'])
def login_view(request):
    """User login page."""
    if request.user.is_authenticated:
        return redirect('todos:list')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # Authenticate using email (stored as username)
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                return redirect('todos:list')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    
    return render(request, 'auth/login.html', {'form': form})


@login_required(login_url='auth:login')
def logout_view(request):
    """User logout."""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('auth:login')


# ============================================================================
# TODO VIEWS (Web Templates with Form Handling)
# ============================================================================

@login_required(login_url='auth:login')
def todo_list(request):
    """Display list of user's todos with filtering options."""
    todos = Todo.objects.filter(user=request.user).order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter in ['pending', 'in_progress', 'completed']:
        todos = todos.filter(status=status_filter)
    
    # Filter by completion
    completed_filter = request.GET.get('completed')
    if completed_filter == 'true':
        todos = todos.filter(completed=True)
    elif completed_filter == 'false':
        todos = todos.filter(completed=False)
    
    context = {
        'todos': todos,
        'status_filter': status_filter,
        'completed_filter': completed_filter,
    }
    return render(request, 'todos/list.html', context)


@login_required(login_url='auth:login')
@require_http_methods(['GET', 'POST'])
def todo_create(request):
    """Create a new todo."""
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            todo = form.save(commit=False)
            todo.user = request.user
            todo.save()
            messages.success(request, 'Todo created successfully!')
            return redirect('todos:list')
    else:
        form = TodoForm()
    
    return render(request, 'todos/create.html', {'form': form})


@login_required(login_url='auth:login')
@require_http_methods(['GET', 'POST'])
def todo_edit(request, todo_id):
    """Edit an existing todo."""
    todo = get_object_or_404(Todo, id=todo_id, user=request.user)
    
    if request.method == 'POST':
        form = TodoForm(request.POST, instance=todo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Todo updated successfully!')
            return redirect('todos:list')
    else:
        form = TodoForm(instance=todo)
    
    return render(request, 'todos/edit.html', {'form': form, 'todo': todo})


@login_required(login_url='auth:login')
@require_http_methods(['POST'])
def todo_delete(request, todo_id):
    """Delete a todo (AJAX endpoint)."""
    todo = get_object_or_404(Todo, id=todo_id, user=request.user)
    todo.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': 'Todo deleted successfully'})
    
    messages.success(request, 'Todo deleted successfully!')
    return redirect('todos:list')


@login_required(login_url='auth:login')
@require_http_methods(['POST'])
def todo_toggle(request, todo_id):
    """Toggle todo completion status (AJAX endpoint)."""
    todo = get_object_or_404(Todo, id=todo_id, user=request.user)
    todo.completed = not todo.completed
    
    # Also update status based on completion
    if todo.completed:
        todo.status = 'completed'
    else:
        todo.status = 'pending'
    
    todo.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'completed': todo.completed,
            'status': todo.status,
        })
    
    return redirect('todos:list')


@login_required(login_url='auth:login')
def todo_stats(request):
    """Display todo statistics."""
    total = Todo.objects.filter(user=request.user).count()
    completed = Todo.objects.filter(user=request.user, completed=True).count()
    pending = total - completed
    
    context = {
        'total': total,
        'completed': completed,
        'pending': pending,
    }
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(context)
    
    return render(request, 'todos/stats.html', context)
