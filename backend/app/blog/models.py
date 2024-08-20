import spacy
from django.db import models
from app.accounts.models import CustomUser
# from app.blog.utils.category_predict import predict_category
from django.utils.text import slugify,Truncator
# Create your models here.
from .choice import PLATFORM_CHOICES

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

#! Category model here
class Category(models.Model):
    name=models.CharField(max_length=100,unique=True)
    meta_title = models.CharField(max_length=100, null=True, blank=True) 
    slug = models.SlugField(unique=True, db_index=True) 
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategories')

    class Meta:
        verbose_name_plural = "Categories"

    def generate_keywords(self):
        doc = nlp(self.name)
        keywords = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]
        return " ".join(keywords)
    def save(self, *args, **kwargs):
        #if not self.meta_title:
            keywords = self.generate_keywords()
            self.meta_title = f"{Truncator(self.name).chars(100)} {keywords}".strip()
        #if not self.slug:
            self.slug = slugify(self.name)
            super().save(*args, **kwargs)
    
    #def save(self, *args, **kwargs):
    #    if not self.slug:
    #        self.slug = slugify(self.name)
    #    if not self.meta_title:
    #        self.meta_title = self.name
    #    super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
#! Tag model here    
class Tag(models.Model):
    name=models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

    

class Post(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    image=models.ImageField(upload_to='post_image')
    content = models.TextField()
    tags=models.ManyToManyField(Tag,blank=True)
    meta_title = models.CharField(max_length=100, null=True, blank=True)  # Added meta_title for SEO
    slug = models.SlugField(unique=True, db_index=True)  # Added slug for URL
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='child_posts')  # Parent post
    summary = models.CharField(max_length=255, null=True, blank=True)  # Added summary for key highlights
    published = models.BooleanField(default=False)  # Added published to identify if the post is publicly available
    category=models.ForeignKey(Category,on_delete=models.SET_NULL,null=True,blank=True,related_name='posts')
    created_at=models.DateTimeField(auto_now_add=True,verbose_name='post_create_date')
    updated_at=models.DateTimeField(auto_now=True,verbose_name='post_update_date')
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='post_publish_date')  # Added published_at for publish date
    class Meta:
        indexes = [
            models.Index(fields=['slug']),  # Custom index for slug
            models.Index(fields=['created_at']),  # Indexing created_at for better query performance
        ]
    def total_likes(self):
        return self.likes.count()
    def total_shares(self):
        return self.shares.count()
    def total_comments(self):
        return self.comments.count()
    def total_bookmarks(self):
        return self.bookmarks.count()
    def generate_keywords(self):
        doc = nlp(self.title)
        keywords = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]
        return " ".join(keywords)
    def save(self, *args, **kwargs):
        #if not self.meta_title:
            keywords = self.generate_keywords()
            self.meta_title = f"{Truncator(self.title).chars(100)} {keywords}".strip()
        #if not self.slug:
            self.slug = slugify(self.title)
            super().save(*args, **kwargs)
    
    #def save(self, *args, **kwargs):
    #         #category_name = predict_category(self.content)
    #         #self.category = Category.objects.get_or_create(name=category_name)[0]
    #         self.slug = slugify(self.title)
    #         self.meta_title = self.title
    #         super().save(*args, **kwargs)
    #def generate_unique_slug(self):
    #    original_slug = slugify(self.title)
    #    queryset = Post.objects.filter(slug=original_slug).exists()
    #    if queryset:
    #        count = 1
    #        while Post.objects.filter(slug=f"{original_slug}-{count}").exists():
    #            count += 1
    #        return f"{original_slug}-{count}"
    #    return original_slug

    def __str__(self):
        return self.title

class Like(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user', 'post') 
    

    def __str__(self):
        return f'{self.user.username} likes {self.post.title}'


class Comment(models.Model):
    author=models.ForeignKey(CustomUser,on_delete=models.CASCADE, related_name='comments')
    post=models.ForeignKey(Post,on_delete=models.CASCADE, related_name='comments')
    content=models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at=models.DateTimeField(auto_now_add=True,verbose_name='post_create_date')
    updated_at=models.DateTimeField(auto_now=True,verbose_name='post_update_date')

    def __str__(self):
        return f'Comment by {self.author} on {self.post}'


class Share(models.Model):

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='shares')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='shares')
    #platform = models.CharField(max_length=50)  # e.g., Facebook, Twitter, etc.
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)  # Added choices for platform
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} shared {self.post.title} on {self.platform}'

class Bookmark(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookmarks')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user', 'post')  # Unique constraint

    def __str__(self):
        return f'{self.user.username} bookmarked {self.post.title}'