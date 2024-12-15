# models.py

from django.db import models

class Author(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    isbn = models.CharField(max_length=13, unique=True)
    available_copies = models.IntegerField(default=0)

    def __str__(self):
        return self.title

class BorrowRecord(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrowed_by = models.CharField(max_length=255)
    borrow_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.book.title} borrowed by {self.borrowed_by}"

# serializers.py

from rest_framework import serializers
from .models import Author, Book, BorrowRecord

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'

class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True) 

    class Meta:
        model = Book
        fields = '__all__'

class BorrowRecordSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)

    class Meta:
        model = BorrowRecord
        fields = '__all__'

# views.py

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import Author, Book, BorrowRecord
from .serializers import AuthorSerializer, BookSerializer, BorrowRecordSerializer
from celery import shared_task

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class BorrowRecordViewSet(viewsets.ModelViewSet):
    queryset = BorrowRecord.objects.all()
    serializer_class = BorrowRecordSerializer

@shared_task
def generate_library_report():
    # Logic to generate the report 
    # (e.g., calculate most borrowed books, 
    # number of books borrowed per month, etc.)
    print("Generating library report...") 
    # Implement your report generation logic here 
    return "Report generated successfully" 

# urls.py

from django.urls import include, path
from rest_framework import routers
from .views import AuthorViewSet, BookViewSet, BorrowRecordViewSet

router = routers.DefaultRouter()
router.register(r'authors', AuthorViewSet)
router.register(r'books', BookViewSet)
router.register(r'borrowrecords', BorrowRecordViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

# celery.py 

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings')  # Replace with your project's settings module

app = Celery('your_project_name')  # Replace with your project's name

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

# settings.py (relevant parts)

CELERY_BROKER_URL = 'redis://localhost:6379'  # Adjust based on your Redis setup
CELERY_RESULT_BACKEND = 'redis://localhost:6379' 

# In your views, you can schedule the task using:
from celery.schedules import crontab
from celery.task import periodic_task

@periodic_task(run_every=crontab(hour=0, minute=0))  # Run daily at midnight
def run_library_report():
    generate_library_report.delay()