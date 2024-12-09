from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, FileUploadForm

# Register view
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'The account {username} was created successfully, now you can login.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


#Profile view
@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        form = FileUploadForm(request.POST, request.FILES)

        if u_form.is_valid and p_form.is_valid() and form.is_valid():
            u_form.save()
            p_form.save()

            uploaded_file = form.cleaned_data['file']

            profile = request.user.profile
            profile.content_type = uploaded_file.content_type 
            profile.content = uploaded_file.read()
            profile.save()
            
            messages.success(request, f'Your account has been updated')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
        form = FileUploadForm()


    context = {
        'u_form': u_form,
        'p_form': p_form,
        'form': form,
    }

    return render(request, 'users/profile.html', context)


def display_image(request):
    return HttpResponse(request.user.profile.content, content_type=request.user.profile.content_type)