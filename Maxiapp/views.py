from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404
from Maxiapp.models import Post, Comment, Category, NewsArticle, UserProfile
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from Maxiapp.forms import CommentForm, SearchForm, ContactForm
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils.safestring import mark_safe
from django.conf import settings
import requests
from django.urls import reverse
from django.core.cache import cache
from django.contrib.auth.decorators import login_required




@login_required
def profile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    return render(request, 'blog/profile.html', {'profile': profile})



def fetch_api_data(url, method='GET', querystring=None, headers=None, payload=None):
    """Helper function to fetch API data."""
    try:
        if method == 'POST':
            response = requests.post(url, json=payload, headers=headers, params=querystring)
        else:
            response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return {}



def save_api_data(data):
    """Helper function to save API data to the database."""
    for item in data:
        published_at = item.get('publishedAt', None)
        if published_at:
            published_at = parse_datetime(published_at)
        else:
            published_at = timezone.now()  # Use current date and time as default

        NewsArticle.objects.update_or_create(
            title=item.get('title', 'No Title'),
            defaults={
                'description': item.get('description', ''),
                'url': item.get('url', ''),
                'source_name': item.get('source', {}).get('name', 'Unknown Source'),
                'published_at': published_at,
                'image_url': item.get('urlToImage', '')
            }
        )


def blog_index(request):
    post_list = Post.objects.all().order_by("?")
    trending_posts = Post.objects.all().order_by('?')
    recent = Post.objects.order_by("-date_created")

    # Initialize variables
    api_news = []
    sports_api = []
    nigeria_news_api = []
    top_news_part = []

    # Cache keys
    api_news_cache_key = 'api_news'
    sports_api_cache_key = 'sports_api'
    nigeria_news_api_cache_key = 'nigeria_news_api'
    top_news_api_cache_key = 'top_news_part'

    # Fetch and cache API data
    api_news = cache.get(api_news_cache_key)
    if not api_news:
        api_news = fetch_api_data(
            url="https://real-time-news-data.p.rapidapi.com/top-headlines",
            querystring={"limit":"500","country":"NG","lang":"en"},
            headers={
                "x-rapidapi-key": "382018f074mshd68d65e447b48bbp1ea843jsn5c162b7f612d",
                "x-rapidapi-host": "real-time-news-data.p.rapidapi.com"
            },
        ).get("data", [])
        cache.set(api_news_cache_key, api_news, timeout=60*60*12)
        save_api_data(api_news)  # Save data to the database

    sports_api = cache.get(sports_api_cache_key)
    if not sports_api:
        sports_api = fetch_api_data(
            url="https://google-news22.p.rapidapi.com/v1/topic-headlines",
            querystring={"country": "ng", "language": "en", "topic": "sports"},
            headers={
                "x-rapidapi-key": "382018f074mshd68d65e447b48bbp1ea843jsn5c162b7f612d",
                "x-rapidapi-host": "google-news22.p.rapidapi.com"
            },
        ).get("data", [])
        cache.set(sports_api_cache_key, sports_api, timeout=60*60*12)
        save_api_data(sports_api)  # Save data to the database

    nigeria_news_api = cache.get(nigeria_news_api_cache_key)
    if not nigeria_news_api:
        nigeria_news_api = fetch_api_data(
            url="https://google-news22.p.rapidapi.com/v1/geolocation",
            querystring={"country": "ng", "language": "en", "location": "Nigeria"},
            headers={
                "x-rapidapi-key": "382018f074mshd68d65e447b48bbp1ea843jsn5c162b7f612d",
                "x-rapidapi-host": "google-news22.p.rapidapi.com"
            },
        ).get("data", [])
        cache.set(nigeria_news_api_cache_key, nigeria_news_api, timeout=60*60*12)
        save_api_data(nigeria_news_api)  # Save data to the database

    top_news_part = cache.get(top_news_api_cache_key)
    if not top_news_part:
        top_news_part = fetch_api_data(
            url="https://google-news22.p.rapidapi.com/v1/top-headlines",
            querystring={"country": "NG", "language": "en"},
            headers={
                "x-rapidapi-key": "382018f074mshd68d65e447b48bbp1ea843jsn5c162b7f612d",
                "x-rapidapi-host": "google-news22.p.rapidapi.com"
            },
        ).get("data", [])
        cache.set(top_news_api_cache_key, top_news_part, timeout=60*60*12)
        save_api_data(top_news_part)  # Save data to the database

    # Pagination
    paginator = Paginator(api_news, 15)
    page_number = request.GET.get('page')
    paginated_api_news = paginator.get_page(page_number)

    # Rendering context
    context = {
        "recent": recent,
        "trending_posts": trending_posts,
        "api_news": paginated_api_news,
        "sports_api": sports_api,
        "nigeria_news_api": nigeria_news_api,
        "top_news_apis": top_news_part,
    }
    return render(request, "blog/index.html", context)


def blog_category(request, category_name):
    category = get_object_or_404(Category, name=category_name)
    category_post = Post.objects.filter(categories=category).order_by("-date_created")
    paginator = Paginator(category_post, 15)
    category_number = request.GET.get('page')
    posts = paginator.get_page(category_number)
    context = {
        "category": category.name,
        "posts": posts,
    }
    return render(request, "blog/category.html", context)


def blog_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    post.increment_views()
    form = CommentForm()
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = Comment(
                author=form.cleaned_data["author"],
                comment=form.cleaned_data["body"],
                post=post,
            )
            comment.save()
            return HttpResponseRedirect(mark_safe(request.path_info))

    comments = Comment.objects.filter(post=post)
    context = {
        "post": post,
        "comments": comments,
        "form": CommentForm(),
    }
    return render(request, "blog/detail.html", context)


def about_us(request):
    return render(request, 'blog/about_us.html')


def terms_of_service(request):
    return render(request, 'blog/terms_of_service.html')


def privacy(request):
    return render(request, 'blog/privacy.html')


def contact_us(request):
    success = False
    if request.method == 'POST':
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            name = contact_form.cleaned_data['name']
            email = contact_form.cleaned_data['email']
            message = contact_form.cleaned_data['message']

            send_mail(
                subject=f"Contact from {name}",
                message=f"Name: {name}\n\nEmail: {email}\n\nMessage: {message}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['nwachukwuclinton2@gmail.com'],
                fail_silently=False,
            )
            success = True
    else:
        contact_form = ContactForm()
    return render(request, 'blog/contact_us.html', {"form": contact_form, "success": success})

def sports(request):
    # Caching keys
    sports_api_cache_key1 = 'sports_api1'
    sports_api_cache_key2 = 'sports_api2'

    sports_api1 = cache.get(sports_api_cache_key1)
    if not sports_api1:
        sports_api1 = fetch_api_data(
            url="https://news-api14.p.rapidapi.com/v2/trendings",
            querystring={"topic": "sports", "language": "en", "country": "ng", "limit": "100"},
            headers={
                "x-rapidapi-key": "382018f074mshd68d65e447b48bbp1ea843jsn5c162b7f612d",
                "x-rapidapi-host": "news-api14.p.rapidapi.com"
            },
        ).get('data', [])
        cache.set(sports_api_cache_key1, sports_api1, timeout=60*60*24)
        save_api_data(sports_api1)

    sports_api2 = cache.get(sports_api_cache_key2)
    if not sports_api2:
        sports_api2 = fetch_api_data(
            url="https://news-api14.p.rapidapi.com/v2/trendings",
            querystring={"topic": "sports", "language": "en", "country": "ng", "limit": "100", "page": "2"},
            headers={
                "x-rapidapi-key": "382018f074mshd68d65e447b48bbp1ea843jsn5c162b7f612d",
                "x-rapidapi-host": "news-api14.p.rapidapi.com"
            },
        ).get('data', [])
        cache.set(sports_api_cache_key2, sports_api2, timeout=60*60*24)
        save_api_data(sports_api2)

    context = {
        "sports_api1": sports_api1,
        "sports_api2": sports_api2,
    }
    return render(request, 'blog/sports.html', context)


def politics(request):
    # Caching keys
    politics_api_cache_key1 = 'politics_api'

    politics_api = cache.get(politics_api_cache_key1)
    if not politics_api:
        politics_api = fetch_api_data(
            url="https://news67.p.rapidapi.com/v2/country-news",
            querystring={"batchSize": "30", "fromCountry": "ng", "languages": "en", "onlyInternational": "true"},
            headers={
                "x-rapidapi-key": "382018f074mshd68d65e447b48bbp1ea843jsn5c162b7f612d",
                "x-rapidapi-host": "news67.p.rapidapi.com"
            },
        ).get('news', [])
        cache.set(politics_api_cache_key1, politics_api, timeout=60*60*12)
        save_api_data(politics_api)

    context = {
        "politics_api": politics_api,
    }
    return render(request, 'blog/politics.html', context)


def entertainment(request):
    # Caching key
    entertainment_api_cache_key = 'entertainment_api'

    entertainment_api = cache.get(entertainment_api_cache_key)
    if not entertainment_api:
        url = "https://newsnow.p.rapidapi.com/newsv2_top_news_cat"
        payload = {
            "category": "ENTERTAINMENT",
            "location": "NG",
            "language": "en",
            "page": 1
        }
        headers = {
            "x-rapidapi-key": "382018f074mshd68d65e447b48bbp1ea843jsn5c162b7f612d",
            "x-rapidapi-host": "newsnow.p.rapidapi.com",
            "Content-Type": "application/json"
        }
        entertainment_api = fetch_api_data(url, method='POST', headers=headers, payload=payload).get('news', [])
        cache.set(entertainment_api_cache_key, entertainment_api, timeout=60*60*24)  # Cache for 24 hours
        save_api_data(entertainment_api)

    context = {
        "entertainment_api": entertainment_api,
    }
    return render(request, 'blog/entertainment.html', context)


def international_news(request):
    # Caching key
    international_news_api_key = 'international_news_api'

    international_news_api = cache.get(international_news_api_key)
    if not international_news_api:
        international_news_api = fetch_api_data(
            url="https://google-news25.p.rapidapi.com/news/list",
            querystring={"category": "CAQiRENCQVNMUW9JTDIwdk1EVnFhR2NTQW1WdUdnSlZVeUlPQ0FRYUNnb0lMMjB2TURsdWJWOHFDUW9IRWdWWGIzSnNaQ2dBKioIAComCAoiIENCQVNFZ29JTDIwdk1EVnFhR2NTQW1WdUdnSlZVeWdBUAFQAQ"},
            headers={
                "x-rapidapi-key": "382018f074mshd68d65e447b48bbp1ea843jsn5c162b7f612d",
                "x-rapidapi-host": "google-news25.p.rapidapi.com"
            },
        ).get('data', [])
        cache.set(international_news_api_key, international_news_api, timeout=60*60*5)
        save_api_data(international_news_api)

    context = {
        "international_news_api": international_news_api,
    }
    return render(request, 'blog/international_news.html', context)



def preprocess_data(data):
    """Helper function to preprocess data."""
    for article in data:
        if 'source name' in article:
            article['source_name'] = article.pop('source name')
    return data


def rush_hour(request):
    # Caching key
    rush_hour_api_cache_key = 'rush_hour_api'

    # Fetch cached rush hour API data
    rush_hour_api = cache.get(rush_hour_api_cache_key)
    if not rush_hour_api:
        url = "https://get-top-news-headlines-by-region.p.rapidapi.com/"
        payload = {
            "country": "NG",
            "region": "Nigeria"
        }
        headers = {
            "x-rapidapi-key": "382018f074mshd68d65e447b48bbp1ea843jsn5c162b7f612d",
            "x-rapidapi-host": "get-top-news-headlines-by-region.p.rapidapi.com",
            "Content-Type": "application/json"
        }
        rush_hour_api = fetch_api_data(url, method='POST', headers=headers, payload=payload).get('article_list', [])
        cache.set(rush_hour_api_cache_key, rush_hour_api, timeout=60*60*12)  # Cache for 12 hours
        save_api_data(rush_hour_api)

    context = {
        "rush_hour_api": rush_hour_api,
    }
    return render(request, 'blog/rush_hour.html', context)



def search(request):
    form = SearchForm()
    query = None
    search_results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']

            # Search in cached data sources
            cached_data_sources = ['api_news', 'sports_api', 'nigeria_news_api', 'top_news_part', "sports_api1", "politics_api", "entertainment_api", "international_news_api"]
            for cache_key in cached_data_sources:
                cached_data = cache.get(cache_key)
                if cached_data:
                    search_results.extend([item for item in cached_data if query.lower() in item['title'].lower()])

    paginator = Paginator(search_results, 15)
    page_number = request.GET.get('page')
    try:
        paginated_search_results = paginator.get_page(page_number)
    except PageNotAnInteger:
        paginated_search_results = paginator.page(1)
    except EmptyPage:
        paginated_search_results = paginator.page(paginator.num_pages)

    context = {
        'form': form,
        'query': query,
        'search_results': paginated_search_results,
    }
    return render(request, 'blog/search.html', context)





def ads_txt_redirect(request):
    return HttpResponseRedirect('https://srv.adstxtmanager.com/19390/focushub.ng')


