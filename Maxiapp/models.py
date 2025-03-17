from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User



class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, null=True)
    image = models.ImageField(upload_to='image')
    image2 = models.ImageField(upload_to='image', blank=True, null=True)
    image3 = models.ImageField(upload_to='image', blank=True, null=True)
    videos = models.FileField(upload_to='videos', blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    body = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)
    categories = models.ManyToManyField(Category, related_name='posts')
    updated_by = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def increment_views(self):
        self.views += 1
        self.save()

    def get_absolute_url(self):
        return reverse('details', args=[str(self.slug)])

    def __str__(self):
        return self.title

class Comment(models.Model):
    author = models.CharField(max_length=100)
    comment = models.TextField()
    comment_made_on = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return self.author



class NewsArticle(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    url = models.URLField()
    source_name = models.CharField(max_length=255)
    published_at = models.DateTimeField()
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def __str__(self):
        return self.user.username


