from django.urls import include, path

from advarisk.users.views import (
    user_detail_view,
    user_redirect_view,
    user_update_view,
)
from advarisk.users import views

app_name = "users"
urlpatterns = [
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("<int:pk>/", view=user_detail_view, name="detail"),
    path('admin/details/', views.my_page_view, name='my_page'),
    path("api/invitation/", views.Invitation.as_view({'post': 'adduser'}), name='refresh'),
    path("api/blockuser/", views.Invitation.as_view({'post': 'blockuser'}), name='refresh'),

]
