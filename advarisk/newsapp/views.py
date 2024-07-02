from django.shortcuts import render
from datetime import timedelta
from django.utils import timezone
import requests
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Keyword, Article
from django.db.models import Max, Count
import os


class KeywordViewSet(viewsets.ModelViewSet):
    """
    A viewset for performing operations on keywords, including search and refresh functionality.
    """
    permission_classes = [IsAuthenticated]

    def search(self, request):
        """
        Perform a search based on the provided keyword and optional filters.
        Cache results and use cached results if available within a 15-minute threshold.

        Parameters:
            request (Request): The request object containing user and search data.

        Returns:
            Response: A response object with the search results or an error message.
        """
        user = request.user
        keyword = request.data.get('keyword')

        if not keyword:
            return Response({"error": "Keyword is required."}, status=status.HTTP_400_BAD_REQUEST)

        date_published = request.data.get('date_published')
        source_name = request.data.get('source_name')
        source_category = request.data.get('source_category')
        article_language = request.data.get('article_language')

        user_keyword, created = Keyword.objects.get_or_create(user=user, keyword=keyword)

        threshold_time = timezone.now() - timedelta(minutes=15)
        if not created and user_keyword.last_searched >= threshold_time:
            articles_query = Article.objects.filter(keyword=user_keyword).first()
            if articles_query:
                return Response(articles_query.articles_list, status=status.HTTP_200_OK)
            else:
                return Response({"error": "You can only search for this keyword after 15 minutes, and no cached results are available."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        api_key = os.getenv('api_key')
        url = f'https://newsapi.org/v2/everything?q={keyword}&sortBy=publishedAt&apiKey={api_key}'

        if date_published:
            url += f'&from={date_published}'
        if source_name:
            url += f'&sources={source_name}'
        if article_language:
            url += f'&language={article_language}'
        if source_category:
            url += f'&category={source_category}'

        response = requests.get(url)
        data = response.json()

        search_results = {
            'last_searched': timezone.now().isoformat(),
            'articles': data.get('articles', [])
        }

        Article.objects.filter(keyword=user_keyword).delete()

        articles_list = []
        for article_data in data.get('articles', []):
            articles_list.append(article_data)

        Article.objects.create(keyword=user_keyword, articles_list=articles_list)

        user_keyword.last_searched = timezone.now()
        if 'articles' in data and data['articles']:
            user_keyword.latest_published_at = data['articles'][0]['publishedAt']
        user_keyword.save()

        return Response(data.get('articles', []), status=status.HTTP_200_OK)

    def refresh(self, request):
        """
        Refresh the search results based on the last searched keyword and its latest published date.

        Parameters:
            request (Request): The request object containing user and keyword data.

        Returns:
            Response: A response object with the refreshed search results or an error message.
        """
        user = request.user
        keyword = request.data.get('keyword')

        if not keyword:
            return Response({"error": "Keyword is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_keyword = Keyword.objects.get(user=user, keyword=keyword)
        except Keyword.DoesNotExist:
            return Response({"error": "Keyword not found."}, status=status.HTTP_404_NOT_FOUND)

        api_key = os.getenv('api_key')
        latest_published_at = user_keyword.latest_published_at
        if not latest_published_at:
            return Response({"error": "No previous search data found to refresh."}, status=status.HTTP_404_NOT_FOUND)

        url = f'https://newsapi.org/v2/everything?q={keyword}&from={latest_published_at}&sortBy=publishedAt&apiKey={api_key}'

        response = requests.get(url)
        data = response.json()

        Article.objects.filter(keyword=user_keyword).delete()

        articles_list = []
        for article_data in data.get('articles', []):
            articles_list.append(article_data)

        Article.objects.create(keyword=user_keyword, articles_list=articles_list)

        if 'articles' in data and data['articles']:
            user_keyword.latest_published_at = data['articles'][0]['publishedAt']
            user_keyword.last_searched = timezone.now()
            user_keyword.save()

        return Response(data.get('articles', []), status=status.HTTP_200_OK)


class BackgroundJob(viewsets.ModelViewSet):
    """
    A viewset for performing background job operations such as automatic refreshing of search results.
    """
    permission_classes = [IsAuthenticated]

    def automatic_refresh_search(self, request):
        """
        Automatically refresh search results for the most trending keywords.

        Parameters:
            request (Request): The request object containing user data.

        Returns:
            Response: A response object with the refreshed search results for trending keywords or an error message.
        """
        max_count = Keyword.objects.values('keyword').annotate(keyword_count=Count(
            'keyword')).aggregate(max_count=Max('keyword_count'))['max_count']

        trending_keywords = Keyword.objects.values('keyword').annotate(
            keyword_count=Count('keyword')).filter(keyword_count=max_count)

        if trending_keywords:
            for trending_keyword in trending_keywords:
                global keyword
                keyword = trending_keyword['keyword']
        else:
            print("No trending keywords found.")

        api_key = os.getenv('api_key')
        url = f'https://newsapi.org/v2/everything?q={keyword}&sortBy=publishedAt&apiKey={api_key}'

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(data)
            finalresponse = {"Trending_keyword": keyword, "data": data.get('articles', [])}
            return Response(finalresponse, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
