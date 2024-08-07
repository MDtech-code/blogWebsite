from django.db import models
from app.accounts.models import CustomUser
from app.blog.utils.category_predict import predict_category

# Create your models here.




    
class Category(models.Model):
    name=models.CharField(max_length=100)
    meta_title = models.CharField(max_length=100, null=True, blank=True) 
    slug = models.SlugField(unique=True) 
    parent_id = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategories')

    def __str__(self):
        return self.name
class Tag(models.Model):
    name=models.CharField(max_length=50)
    def __str__(self):
        return self.name

    

class Post(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    image=models.ImageField(upload_to='post_image')
    content = models.TextField()
    tags=models.ManyToManyField(Tag,blank=True)
    meta_title = models.CharField(max_length=100, null=True, blank=True)  # Added meta_title for SEO
    slug = models.SlugField(unique=True)  # Added slug for URL
    parent_id = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='child_posts')  # Parent post
    summary = models.CharField(max_length=255, null=True, blank=True)  # Added summary for key highlights
    published = models.BooleanField(default=False)  # Added published to identify if the post is publicly available
    category=models.ForeignKey(Category,on_delete=models.SET_NULL,null=True,blank=True,related_name='posts')
    created_at=models.DateTimeField(auto_now_add=True,verbose_name='post_create_date')
    updated_at=models.DateTimeField(auto_now=True,verbose_name='post_update_date')
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='post_publish_date')  # Added published_at for publish date

    def total_likes(self):
        return self.likes.count()
    
    def save(self, *args, **kwargs):
        if not self.category:
            category_name = predict_category(self.content)
            self.category = Category.objects.get_or_create(name=category_name)[0]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Like(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f'{self.user.username} likes {self.post.title}'


class Comment(models.Model):
    author=models.ForeignKey(CustomUser,on_delete=models.CASCADE, related_name='conments')
    post=models.ForeignKey(Post,on_delete=models.CASCADE, related_name='conments')
    content=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True,verbose_name='post_create_date')
    updated_at=models.DateTimeField(auto_now=True,verbose_name='post_update_date')

    def __str__(self):
        return f'Comment by {self.author} on {self.post}'


class Share(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='shares')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='shares')
    platform = models.CharField(max_length=50)  # e.g., Facebook, Twitter, etc.
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} shared {self.post.title} on {self.platform}'

class Bookmark(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookmarks')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} bookmarked {self.post.title}'