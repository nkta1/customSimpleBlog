from django.template.response import TemplateResponse
from django.shortcuts import redirect
from blogApp.models import *
import hashlib
import random
import string


# Main page
def posts(request):
    user = get_user_token_from_cookie(request)
    all_posts = Post.objects.all()  # Get all posts
    if user is None:
        interface = enable_auth_interface(False)
        return TemplateResponse(request, 'posts.html', {'entry': interface, 'posts': all_posts})
    else:
        interface = enable_auth_interface(True)
        current_user = Person.objects.get(token=user)  # Find user by token
        if current_user.status == 'admin':
            return TemplateResponse(request, 'posts.html', {'entry': interface, 'posts': all_posts, 'status': 'admin'})
        else:
            return TemplateResponse(request, 'posts.html', {'entry': interface, 'posts': all_posts})


# Login page
def login(request):
    user = get_user_token_from_cookie(request)
    if user is None:
        interface = enable_auth_interface(False)
        if request.method == 'GET':
            return TemplateResponse(request, 'login.html', {'entry': interface})
        elif request.method == 'POST':
            login = request.POST.get('login')
            password = request.POST.get('password')
            hashed_password = hash_data(password)
            user = find_user_by_login(login)  # Find user by login

            if user:
                if check_user_password(user, hashed_password):
                    user.token = generate_user_token()  # Generate and save user token
                    # Save user token to have an authorized access to web pages
                    user.save()
                    response = save_in_cookie(request, user.token)
                else:
                    error = 'Неверный пароль!'
                    response = TemplateResponse(request, 'login.html', {'error': error, 'entry': interface})
            else:
                error = 'Пользователь с таким логином не найден!'
                response = TemplateResponse(request, 'login.html', {'error': error, 'entry': interface})
            return response
    else:
        return logout(request)


# Create new post (only admin)
def create_post(request):
    user_token = get_user_token_from_cookie(request)
    if user_token is not None:
        interface = enable_auth_interface(True)
        user = Person.objects.get(token=user_token)  # Find user by token
        if user.status != 'admin':
            return redirect('posts')
        else:
            if request.method == 'POST':
                # Create new post
                post_title = request.POST.get('post-title')
                post_content = request.POST.get('post-content')
                new_post = Post(name=post_title, content=post_content)
                new_post.save()
        return TemplateResponse(request, 'createpost.html', {'entry': interface, 'status': 'admin'})
    else:
        return redirect('posts')


# Enable some interface when user is authorized
def enable_auth_interface(is_authorized):
    if is_authorized:
        interface = 'Выйти'
    else:
        interface = 'Войти'
    return interface


# Logout from the system
def logout(request):
    response = redirect('posts')  # Object to save cookie
    response.set_cookie("s-blog_token", '', max_age=0)  # Delete current token from cookie
    return response


# Save user token in cookie
def save_in_cookie(request, user_token):
    response = redirect('posts')  # Object to save cookie
    response.set_cookie("s-blog_token", user_token)
    return response


# Get token from cookie file
def get_user_token_from_cookie(request):
    if "s-blog_token" in request.COOKIES:
        return request.COOKIES['s-blog_token']
    else:
        return None


# Hash data with sha256
def hash_data(data):
    return hashlib.sha256(data.encode()).hexdigest()


# Getting Profile object by login primary key
def find_user_by_login(user_login):
    try:
        user = Person.objects.get(login=user_login)
        return user
    except:
        return None


# Check user password
def check_user_password(user, user_password):
    if user.password == user_password:
        return 1
    else:
        return None


# Generate unique user token from ascii (30 characters)
def generate_user_token():
    generated_token = ''.join(random.choice(string.ascii_letters) for i in range(30))
    try:
        user = Person.objects.get(token=generated_token)
    except:
        user = None
    if user is None:
        return generated_token
    else:
        return generate_user_token()
