from django.urls import path
from . import views
from .views import profile


urlpatterns = [
    path("", views.blog_index, name="Home"),
    path("post/<slug:slug>/", views.blog_detail, name="details"),
    path("category/<str:category_name>/", views.blog_category, name="category"),
    path("search/", views.search, name="search"),
    path("About/", views.about_us, name="About us"),
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms_of_service, name="terms of service"),
    path('contact_us/', views.contact_us, name="Contact us"),
    path("sports/", views.sports, name="sports"),
    path("politics/", views.politics, name="politics"),
    path("Entertainment/", views.entertainment, name="entertainment news"),
    path("world news/", views.international_news, name="international news"),
    path("Rush Hours/", views.rush_hour, name="rush hour"),
    path('profile/', profile, name='profile'),


]
