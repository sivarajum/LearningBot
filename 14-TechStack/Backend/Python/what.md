# Python Backend Development Guide

## What is Python Backend Development?

Python backend development involves creating server-side applications, APIs, and services using Python. Python is widely used for backend development due to its simplicity, extensive libraries, and strong community support.

### Key Characteristics

- **Versatile**: Web applications, APIs, microservices, data processing
- **Rich Ecosystem**: Extensive libraries and frameworks
- **Scalable**: From small scripts to large enterprise applications
- **Integration**: Works well with databases, message queues, and other services
- **Rapid Development**: Quick prototyping and development cycles

## Core Frameworks

### Flask

Flask is a lightweight WSGI web application framework designed to make getting started quick and easy.

#### Basic Flask Application

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

# Basic route
@app.route('/')
def hello():
    return 'Hello, World!'

# Route with parameters
@app.route('/user/<username>')
def show_user_profile(username):
    return f'User: {username}'

# Route with HTTP methods
@app.route('/api/data', methods=['GET', 'POST'])
def handle_data():
    if request.method == 'POST':
        data = request.get_json()
        # Process data
        return jsonify({'message': 'Data received', 'data': data})
    else:
        return jsonify({'message': 'GET request received'})

# Route with query parameters
@app.route('/search')
def search():
    query = request.args.get('q', '')
    limit = request.args.get('limit', 10, type=int)
    return jsonify({
        'query': query,
        'limit': limit,
        'results': []  # Mock results
    })

if __name__ == '__main__':
    app.run(debug=True)
```

#### Flask with SQLAlchemy

```python
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }

# Create tables
with app.app_context():
    db.create_all()

# CRUD operations
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()

    # Validation
    if not data or not data.get('username') or not data.get('email'):
        return jsonify({'error': 'Username and email are required'}), 400

    # Check if user exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 409

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 409

    user = User(username=data['username'], email=data['email'])
    db.session.add(user)
    db.session.commit()

    return jsonify(user.to_dict()), 201

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Update fields
    if 'username' in data:
        # Check if new username is taken by another user
        existing = User.query.filter_by(username=data['username']).first()
        if existing and existing.id != user_id:
            return jsonify({'error': 'Username already exists'}), 409
        user.username = data['username']

    if 'email' in data:
        # Check if new email is taken by another user
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user_id:
            return jsonify({'error': 'Email already exists'}), 409
        user.email = data['email']

    db.session.commit()
    return jsonify(user.to_dict())

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)
```

#### Flask with JWT Authentication

```python
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, create_refresh_token,
    jwt_refresh_token_required
)
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///auth.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }

# Create tables
with app.app_context():
    db.create_all()

# Authentication routes
@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Username, email, and password are required'}), 400

    # Check if user exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 409

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 409

    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict()
    }), 201

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password are required'}), 400

    user = User.query.filter_by(username=data['username']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401

    if not user.is_active:
        return jsonify({'error': 'Account is deactivated'}), 401

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    })

@app.route('/auth/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    return jsonify({'access_token': access_token})

@app.route('/auth/profile', methods=['GET'])
@jwt_required
def get_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    return jsonify(user.to_dict())

@app.route('/auth/profile', methods=['PUT'])
@jwt_required
def update_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Update fields (excluding password for now)
    if 'email' in data:
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user.id:
            return jsonify({'error': 'Email already exists'}), 409
        user.email = data['email']

    db.session.commit()
    return jsonify(user.to_dict())

if __name__ == '__main__':
    app.run(debug=True)
```

### Django

Django is a high-level Python web framework that encourages rapid development and clean, pragmatic design.

#### Django Project Structure

```
myproject/
├── manage.py
├── myproject/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   └── myapp/
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── models.py
│       ├── tests.py
│       ├── urls.py
│       ├── views.py
│       └── migrations/
└── requirements.txt
```

#### Django Models

```python
# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class CustomUser(AbstractUser):
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.username

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

class Post(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    excerpt = models.TextField(blank=True)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    tags = models.ManyToManyField('Tag', blank=True, related_name='posts')

    class Meta:
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    color = models.CharField(max_length=7, default='#007bff')  # Hex color

    def __str__(self):
        return self.name

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'
```

#### Django Views

```python
# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

from .models import Post, Category, Tag, Comment
from .forms import PostForm, CommentForm

# Function-based views
def home(request):
    posts = Post.objects.filter(status='published').order_by('-published_at')[:10]
    categories = Category.objects.all()
    return render(request, 'blog/home.html', {
        'posts': posts,
        'categories': categories
    })

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    comments = post.comments.filter(is_approved=True)

    if request.method == 'POST' and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post_detail', slug=slug)
    else:
        form = CommentForm()

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form
    })

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()  # Save many-to-many relationships
            return redirect('post_detail', slug=post.slug)
    else:
        form = PostForm()

    return render(request, 'blog/post_form.html', {'form': form})

# Class-based views
class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = Post.objects.filter(status='published')

        # Filter by category
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # Filter by tag
        tag_slug = self.request.GET.get('tag')
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)

        # Search
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                models.Q(title__icontains=search_query) |
                models.Q(content__icontains=search_query) |
                models.Q(excerpt__icontains=search_query)
            )

        return queryset.order_by('-published_at')

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return Post.objects.filter(status='published')

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('post_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('post_list')

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)

# API views
@csrf_exempt
@require_POST
def api_create_comment(request, post_id):
    try:
        data = json.loads(request.body)
        post = get_object_or_404(Post, id=post_id, status='published')

        comment = Comment.objects.create(
            post=post,
            author=request.user if request.user.is_authenticated else None,
            content=data['content']
        )

        return JsonResponse({
            'id': comment.id,
            'content': comment.content,
            'author': comment.author.username if comment.author else 'Anonymous',
            'created_at': comment.created_at.isoformat()
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def api_posts(request):
    posts = Post.objects.filter(status='published').order_by('-published_at')[:20]
    data = [{
        'id': post.id,
        'title': post.title,
        'slug': post.slug,
        'excerpt': post.excerpt,
        'author': post.author.username,
        'published_at': post.published_at.isoformat() if post.published_at else None,
        'category': post.category.name if post.category else None,
        'tags': [tag.name for tag in post.tags.all()]
    } for post in posts]

    return JsonResponse({'posts': data})
```

#### Django REST Framework

```python
# serializers.py
from rest_framework import serializers
from .models import Post, Category, Tag, Comment, CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'bio', 'location']
        read_only_fields = ['id']

class CategorySerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'post_count']

    def get_post_count(self, obj):
        return obj.posts.filter(status='published').count()

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'color']

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'created_at', 'is_approved']
        read_only_fields = ['id', 'created_at']

class PostListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'excerpt', 'content', 'author',
            'category', 'tags', 'status', 'published_at', 'comment_count'
        ]
        read_only_fields = ['id', 'slug', 'published_at']

    def get_comment_count(self, obj):
        return obj.comments.filter(is_approved=True).count()

class PostDetailSerializer(PostListSerializer):
    comments = CommentSerializer(many=True, read_only=True, source='comments.filter(is_approved=True)')

    class Meta(PostListSerializer.Meta):
        fields = PostListSerializer.Meta.fields + ['comments']

# views.py (DRF)
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Post, Comment
from .serializers import PostListSerializer, PostDetailSerializer, CommentSerializer
from .permissions import IsAuthorOrReadOnly

class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.filter(status='published')
    serializer_class = PostListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.filter(status='published')
    serializer_class = PostDetailSerializer
    permission_classes = [IsAuthorOrReadOnly]

class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs['post_id'], status='published')
        serializer.save(author=self.request.user, post=post)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')

    # Assuming we have a many-to-many relationship for likes
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True

    return Response({
        'liked': liked,
        'like_count': post.likes.count()
    })

# Custom API view
class PostStatsView(APIView):
    def get(self, request):
        total_posts = Post.objects.filter(status='published').count()
        total_comments = Comment.objects.filter(is_approved=True).count()
        total_users = CustomUser.objects.count()

        # Posts per month (last 12 months)
        from django.db.models import Count
        from django.db.models.functions import TruncMonth
        from datetime import datetime, timedelta

        twelve_months_ago = datetime.now() - timedelta(days=365)
        monthly_stats = Post.objects.filter(
            status='published',
            published_at__gte=twelve_months_ago
        ).annotate(
            month=TruncMonth('published_at')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')

        return Response({
            'total_posts': total_posts,
            'total_comments': total_comments,
            'total_users': total_users,
            'monthly_stats': list(monthly_stats)
        })
```

#### Django Settings

```python
# settings.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'corsheaders',
    'django_filters',

    # Local apps
    'blog.apps.BlogConfig',
    'accounts.apps.AccountsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'myproject.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'myproject'),
        'USER': os.environ.get('DB_USER', 'myuser'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'mypassword'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'accounts.CustomUser'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ],
}

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

### FastAPI

FastAPI is a modern, fast web framework for building APIs with Python 3.7+ based on standard Python type hints.

#### Basic FastAPI Application

```python
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
import uvicorn

app = FastAPI(
    title="Blog API",
    description="A simple blog API built with FastAPI",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool = True
    created_at: datetime

    class Config:
        orm_mode = True

class PostBase(BaseModel):
    title: str
    content: str
    excerpt: Optional[str] = None

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    author_id: int
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    post_id: int
    author_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Mock database (in production, use SQLAlchemy or similar)
users_db = {}
posts_db = {}
comments_db = {}
user_counter = 1
post_counter = 1
comment_counter = 1

# Dependency
def get_current_user(user_id: int = Query(..., description="User ID")):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    return users_db[user_id]

# Routes
@app.get("/")
async def root():
    return {"message": "Welcome to the Blog API"}

@app.post("/users/", response_model=User)
async def create_user(user: UserCreate):
    global user_counter

    # Check if username or email already exists
    for existing_user in users_db.values():
        if existing_user["username"] == user.username:
            raise HTTPException(status_code=400, detail="Username already registered")
        if existing_user["email"] == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")

    user_dict = user.dict()
    user_dict["id"] = user_counter
    user_dict["is_active"] = True
    user_dict["created_at"] = datetime.utcnow()

    users_db[user_counter] = user_dict
    user_counter += 1

    return user_dict

@app.get("/users/", response_model=List[User])
async def get_users(skip: int = 0, limit: int = 100):
    users = list(users_db.values())[skip: skip + limit]
    return users

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    return users_db[user_id]

@app.post("/posts/", response_model=Post)
async def create_post(post: PostCreate, author_id: int = Query(..., description="Author ID")):
    global post_counter

    if author_id not in users_db:
        raise HTTPException(status_code=404, detail="Author not found")

    post_dict = post.dict()
    post_dict["id"] = post_counter
    post_dict["author_id"] = author_id
    post_dict["published_at"] = datetime.utcnow()
    post_dict["created_at"] = datetime.utcnow()
    post_dict["updated_at"] = datetime.utcnow()

    posts_db[post_counter] = post_dict
    post_counter += 1

    return post_dict

@app.get("/posts/", response_model=List[Post])
async def get_posts(skip: int = 0, limit: int = 100):
    posts = list(posts_db.values())[skip: skip + limit]
    return posts

@app.get("/posts/{post_id}", response_model=Post)
async def get_post(post_id: int):
    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail="Post not found")
    return posts_db[post_id]

@app.put("/posts/{post_id}", response_model=Post)
async def update_post(post_id: int, post_update: PostCreate):
    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail="Post not found")

    post_dict = posts_db[post_id]
    update_data = post_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        post_dict[field] = value

    post_dict["updated_at"] = datetime.utcnow()
    posts_db[post_id] = post_dict

    return post_dict

@app.delete("/posts/{post_id}")
async def delete_post(post_id: int):
    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail="Post not found")

    del posts_db[post_id]
    return {"message": "Post deleted successfully"}

@app.post("/posts/{post_id}/comments/", response_model=Comment)
async def create_comment(post_id: int, comment: CommentCreate, author_id: int = Query(..., description="Author ID")):
    global comment_counter

    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail="Post not found")

    if author_id not in users_db:
        raise HTTPException(status_code=404, detail="Author not found")

    comment_dict = comment.dict()
    comment_dict["id"] = comment_counter
    comment_dict["post_id"] = post_id
    comment_dict["author_id"] = author_id
    comment_dict["created_at"] = datetime.utcnow()

    comments_db[comment_counter] = comment_dict
    comment_counter += 1

    return comment_dict

@app.get("/posts/{post_id}/comments/", response_model=List[Comment])
async def get_post_comments(post_id: int):
    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail="Post not found")

    comments = [comment for comment in comments_db.values() if comment["post_id"] == post_id]
    return comments

# Advanced endpoints
@app.get("/search/posts/")
async def search_posts(q: str = Query(..., min_length=1), skip: int = 0, limit: int = 100):
    """Search posts by title or content"""
    results = []
    query = q.lower()

    for post in posts_db.values():
        if query in post["title"].lower() or query in post["content"].lower():
            results.append(post)

    return results[skip: skip + limit]

@app.get("/users/{user_id}/posts/", response_model=List[Post])
async def get_user_posts(user_id: int):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")

    user_posts = [post for post in posts_db.values() if post["author_id"] == user_id]
    return user_posts

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### FastAPI with SQLAlchemy

```python
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from passlib.context import CryptContext
import databases
import sqlalchemy

# Database setup
DATABASE_URL = "sqlite:///./blog.db"
database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# SQLAlchemy models
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="author")

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    excerpt = Column(Text, nullable=True)
    author_id = Column(Integer, ForeignKey("users.id"))
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    post_id = Column(Integer, ForeignKey("posts.id"))
    author_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")

# Pydantic models
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool = True
    created_at: datetime

    class Config:
        orm_mode = True

class PostBase(BaseModel):
    title: str
    content: str
    excerpt: Optional[str] = None

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    author_id: int
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    post_id: int
    author_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# FastAPI app
app = FastAPI()

# Database connection
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Helper functions
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

# Routes
@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.post("/users/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if username exists
    db_user = get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Check if email exists
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/", response_model=List[User])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/posts/", response_model=Post)
def create_post(post: PostCreate, author_id: int, db: Session = Depends(get_db)):
    # Check if author exists
    author = db.query(User).filter(User.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    db_post = Post(**post.dict(), author_id=author_id, published_at=datetime.utcnow())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@app.get("/posts/", response_model=List[Post])
def get_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    posts = db.query(Post).offset(skip).limit(limit).all()
    return posts

@app.get("/posts/{post_id}", response_model=Post)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.put("/posts/{post_id}", response_model=Post)
def update_post(post_id: int, post_update: PostCreate, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    for field, value in post_update.dict(exclude_unset=True).items():
        setattr(post, field, value)

    post.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(post)
    return post

@app.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    db.delete(post)
    db.commit()
    return {"message": "Post deleted successfully"}

@app.post("/posts/{post_id}/comments/", response_model=Comment)
def create_comment(post_id: int, comment: CommentCreate, author_id: int, db: Session = Depends(get_db)):
    # Check if post exists
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Check if author exists
    author = db.query(User).filter(User.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    db_comment = Comment(**comment.dict(), post_id=post_id, author_id=author_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@app.get("/posts/{post_id}/comments/", response_model=List[Comment])
def get_post_comments(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    return post.comments

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Database Integration

#### SQLAlchemy Setup

```python
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import os

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///app.db')

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=True  # Set to False in production
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create scoped session for thread safety
db_session = scoped_session(SessionLocal)

# Base class for models
Base = declarative_base()
metadata = Base.metadata

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Drop all tables
def drop_tables():
    Base.metadata.drop_all(bind=engine)

# Initialize database
def init_db():
    create_tables()

if __name__ == "__main__":
    init_db()
```

#### PostgreSQL Connection

```python
import psycopg2
from psycopg2.extras import RealDictCursor
import os

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'myapp'),
        user=os.getenv('DB_USER', 'myuser'),
        password=os.getenv('DB_PASSWORD', 'mypassword'),
        port=os.getenv('DB_PORT', '5432')
    )

def execute_query(query, params=None, fetch=True):
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params or ())
            if fetch:
                result = cursor.fetchall()
                return result
            else:
                conn.commit()
                return cursor.rowcount
    finally:
        conn.close()

# Example usage
def get_users():
    query = "SELECT id, username, email, created_at FROM users ORDER BY created_at DESC"
    return execute_query(query)

def create_user(username, email, password_hash):
    query = """
    INSERT INTO users (username, email, password_hash, created_at)
    VALUES (%s, %s, %s, NOW())
    RETURNING id, username, email, created_at
    """
    return execute_query(query, (username, email, password_hash))

def get_user_by_username(username):
    query = "SELECT * FROM users WHERE username = %s"
    result = execute_query(query, (username,))
    return result[0] if result else None
```

### Testing

#### Flask Testing

```python
import pytest
from flask import json
from app import create_app, db
from app.models import User, Post

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

def test_create_user(client):
    response = client.post('/users', json={
        'username': 'testuser',
        'email': 'test@example.com'
    })
    assert response.status_code == 201

    data = json.loads(response.data)
    assert data['username'] == 'testuser'
    assert data['email'] == 'test@example.com'
    assert 'id' in data

def test_get_users(client):
    # Create a test user first
    client.post('/users', json={
        'username': 'testuser',
        'email': 'test@example.com'
    })

    response = client.get('/users')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['username'] == 'testuser'

def test_get_user_not_found(client):
    response = client.get('/users/999')
    assert response.status_code == 404

def test_create_post(client):
    # Create a user first
    user_response = client.post('/users', json={
        'username': 'author',
        'email': 'author@example.com'
    })
    user_data = json.loads(user_response.data)

    # Create a post
    response = client.post('/posts', json={
        'title': 'Test Post',
        'content': 'This is a test post content.',
        'author_id': user_data['id']
    })
    assert response.status_code == 201

    data = json.loads(response.data)
    assert data['title'] == 'Test Post'
    assert data['content'] == 'This is a test post content.'
    assert data['author_id'] == user_data['id']

def test_update_post(client):
    # Create user and post
    user_response = client.post('/users', json={
        'username': 'author',
        'email': 'author@example.com'
    })
    user_data = json.loads(user_response.data)

    post_response = client.post('/posts', json={
        'title': 'Original Title',
        'content': 'Original content.',
        'author_id': user_data['id']
    })
    post_data = json.loads(post_response.data)

    # Update the post
    response = client.put(f'/posts/{post_data["id"]}', json={
        'title': 'Updated Title',
        'content': 'Updated content.'
    })
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data['title'] == 'Updated Title'
    assert data['content'] == 'Updated content.'

def test_delete_post(client):
    # Create user and post
    user_response = client.post('/users', json={
        'username': 'author',
        'email': 'author@example.com'
    })
    user_data = json.loads(user_response.data)

    post_response = client.post('/posts', json={
        'title': 'Post to Delete',
        'content': 'This post will be deleted.',
        'author_id': user_data['id']
    })
    post_data = json.loads(post_response.data)

    # Delete the post
    response = client.delete(f'/posts/{post_data["id"]}')
    assert response.status_code == 204

    # Verify it's gone
    response = client.get(f'/posts/{post_data["id"]}')
    assert response.status_code == 404
```

#### FastAPI Testing

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Setup: Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Teardown: Drop tables
    Base.metadata.drop_all(bind=engine)

def test_create_user():
    response = client.post(
        "/users/",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_get_users():
    # Create a user first
    client.post(
        "/users/",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword"
        }
    )

    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["username"] == "testuser"

def test_get_user():
    # Create a user first
    create_response = client.post(
        "/users/",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword"
        }
    )
    user_id = create_response.json()["id"]

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["id"] == user_id

def test_get_user_not_found():
    response = client.get("/users/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

def test_create_post():
    # Create a user first
    user_response = client.post(
        "/users/",
        json={
            "username": "author",
            "email": "author@example.com",
            "password": "testpassword"
        }
    )
    user_id = user_response.json()["id"]

    # Create a post
    response = client.post(
        "/posts/",
        json={
            "title": "Test Post",
            "content": "This is a test post content."
        },
        params={"author_id": user_id}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Post"
    assert data["content"] == "This is a test post content."
    assert data["author_id"] == user_id

def test_update_post():
    # Create user and post
    user_response = client.post(
        "/users/",
        json={
            "username": "author",
            "email": "author@example.com",
            "password": "testpassword"
        }
    )
    user_id = user_response.json()["id"]

    post_response = client.post(
        "/posts/",
        json={
            "title": "Original Title",
            "content": "Original content."
        },
        params={"author_id": user_id}
    )
    post_id = post_response.json()["id"]

    # Update the post
    response = client.put(
        f"/posts/{post_id}",
        json={
            "title": "Updated Title",
            "content": "Updated content."
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["content"] == "Updated content."

def test_delete_post():
    # Create user and post
    user_response = client.post(
        "/users/",
        json={
            "username": "author",
            "email": "author@example.com",
            "password": "testpassword"
        }
    )
    user_id = user_response.json()["id"]

    post_response = client.post(
        "/posts/",
        json={
            "title": "Post to Delete",
            "content": "This post will be deleted."
        },
        params={"author_id": user_id}
    )
    post_id = post_response.json()["id"]

    # Delete the post
    response = client.delete(f"/posts/{post_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Post deleted successfully"

    # Verify it's gone
    response = client.get(f"/posts/{post_id}")
    assert response.status_code == 404

def test_create_comment():
    # Create user and post
    user_response = client.post(
        "/users/",
        json={
            "username": "author",
            "email": "author@example.com",
            "password": "testpassword"
        }
    )
    user_id = user_response.json()["id"]

    post_response = client.post(
        "/posts/",
        json={
            "title": "Test Post",
            "content": "Test content."
        },
        params={"author_id": user_id}
    )
    post_id = post_response.json()["id"]

    # Create a comment
    response = client.post(
        f"/posts/{post_id}/comments/",
        json={"content": "This is a test comment."},
        params={"author_id": user_id}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "This is a test comment."
    assert data["post_id"] == post_id
    assert data["author_id"] == user_id
```

This comprehensive guide covers Python backend development with Flask, Django, and FastAPI, including database integration, authentication, testing, and deployment patterns.
