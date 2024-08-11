from .models import Category,Tag,Post,Like,Comment,Share,Bookmark
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers


#! Category  Serializer here

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields=['id','name']

#! Tag  Serializer here
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model=Tag
        fields='__all__'



#! Post Serializer here

from rest_framework import serializers
from .models import Post, Tag

class PostSerializer(serializers.ModelSerializer):
    tags = serializers.CharField()
    total_likes = serializers.IntegerField(read_only=True)
    total_shares=serializers.IntegerField(read_only=True)
    total_comments=serializers.IntegerField(read_only=True)
    total_bookmarks=serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = ['title', 'image', 'content', 'tags', 'summary','total_likes','total_shares','total_comments','total_bookmarks']

    def create(self, validated_data):
        request = self.context.get('request')  # Access the current logged-in user
        if not request:
            raise serializers.ValidationError("Request context is required")

        user = request.user
        tags_data = validated_data.pop('tags', '')  # Get the tag data from validated_data and remove it

        # Split the tags string into a list of individual tags
        tags_list = [tag.strip('#') for tag in tags_data.split() if tag]

        post = Post.objects.create(author=user, **validated_data)  # Create the post instance

        # Add tags to the post
        for tag_name in tags_list:
            tag_instance, created = Tag.objects.get_or_create(name=tag_name)
            post.tags.add(tag_instance)

        return post
    def update(self, instance, validated_data):
     tags_data = validated_data.pop('tags', '')  # Get the tag data from validated_data and remove it

     # Split the tags string into a list of individual tags
     tags_list = [tag.strip('#') for tag in tags_data.split() if tag]

     # Create or get tag instances
     tag_instances = []
     for tag_name in tags_list:
        tag_instance, created = Tag.objects.get_or_create(name=tag_name)
        tag_instances.append(tag_instance)

     # Set the tags for the instance
     instance.tags.set(tag_instances)

    # Update other fields
     for attr, value in validated_data.items():
         setattr(instance, attr, value)
     instance.save()
     return instance

        


#! Post published seriliazer
class PublishedPostSerializer(serializers.ModelSerializer):
    class Meta:
        model=Post
        fields=['published','published_at']
        read_only_fields=['published_at']
#! all post by user 
class AllPostByUserSerializer(serializers.ModelSerializer):
    total_likes = serializers.IntegerField(read_only=True)
    class Meta:
        model=Post
        fields="__all__"

#! likes modle serializer
class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model=Like
        fields='__all__'

#! comments model serializer
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Comment
        fields='__all__'
#! share model serializer
class ShareSerializer(serializers.ModelSerializer):
    class Meta:
        model=Share
        fields='__all__'
#! bookmark model serializer..
class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model=Bookmark
        fields='__all__'