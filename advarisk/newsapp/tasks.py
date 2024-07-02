
import os
from config import celery_app
from celery import shared_task
from .models import Keyword
from django.db.models import Max
from django.db.models import Count
import os
import json
from datetime import datetime, timedelta
from django.utils import timezone
import requests
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .models import Keyword,Article
import os
from dotenv import load_dotenv

@shared_task()
def automatic_refresh_search():
    max_count = Keyword.objects.values('keyword').annotate(keyword_count=Count('keyword')).aggregate(max_count=Max('keyword_count'))['max_count']
    trending_keywords = Keyword.objects.values('keyword').annotate(keyword_count=Count('keyword')).filter(keyword_count=max_count)

    if trending_keywords:
        # Assuming you want to fetch data for the first trending keyword
        keyword = trending_keywords[0]['keyword']
    else:
        print("No trending keywords found.")
        return {"message": "No trending keywords found."}

    api_key = os.getenv('api_key')
    url = f'https://newsapi.org/v2/everything?q={keyword}&sortBy=publishedAt&apiKey={api_key}'

    response = requests.get(url)
    print(response.json())
    if response.status_code == 200:
        data = response.json()
        articles = data.get('articles', [])
        
        # Save articles to database or process further if needed
        if articles:
            print(f"Skipping article without a valid ID: {articles}")
        else:
            print(f"Skipping article without a valid ID: {articles}")
