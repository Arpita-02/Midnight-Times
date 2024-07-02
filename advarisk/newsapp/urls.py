from django.urls import path

from advarisk.newsapp import views


urlpatterns = [
    path("api/search/", views.KeywordViewSet.as_view({'post': 'search'}), name='search'),
    path("api/refresh/", views.KeywordViewSet.as_view({'post': 'refresh'}), name='refresh'),
    path("api/background_search/",
         views.BackgroundJob.as_view({'post': 'automatic_refresh_search'}), name='automatic_refresh_search'),
]
