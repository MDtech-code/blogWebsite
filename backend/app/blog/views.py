
#! django own import 
from django.shortcuts import get_object_or_404

#! DRF components for API handling
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import PostSerializer,PublishedPostSerializer,AllPostByUserSerializer,LikeSerializer,CommentSerializer,BookmarkSerializer,CategorySerializer
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
#! modles
from .models import Post,Like,Comment,Share,Bookmark,Category

#! import related to date and time
from django.utils import timezone
#! utils
from app.blog.utils.share_link import generate_share_url

#! readall category view here..
class CategoryReadView(APIView):
    permission_classes=[AllowAny]
    def get(self,request):
        try:
            category=Category.objects.all()
            serializer=CategorySerializer(category,many=True)
            return Response({'response':serializer.data},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#! post model CURD view here....
class CreatePostView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
             serializer=PostSerializer(data=request.data,context={'request':request})
             if serializer.is_valid():
                serializer.save()
                return Response({'response':'post create sucessfully'},status=status.HTTP_201_CREATED)
             return  Response({'errors': serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
            
#! read all post for everyone
class ReadAllPostView(APIView):
    permission_classes=[AllowAny]
    def get(slef,request):
        try:
            #post=Post.objects.filter(published=True)
            posts = Post.objects.filter(published=True).select_related('author', 'category').prefetch_related('tags')
            serializers=PostSerializer(posts,many=True)
            return Response(serializers.data)
        except Exception as e:
             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
#! read all post for login user
class ReadUserAllPostView(APIView):
    permission_classes=[IsAuthenticated]
    def get(slef,request):
        try:
            #post=Post.objects.filter(author=request.user)
            posts = Post.objects.filter(author=request.user).select_related('author', 'category').prefetch_related('tags')
            serializers=AllPostByUserSerializer(posts,many=True)
            return Response(serializers.data, status=status.HTTP_200_OK)
        except Exception as e:
             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
#! read post for specific categorey
class PostsByCategoryView(APIView):
    permission_classes=[AllowAny]
    def get(self,request,category_slug):
        try:
             category = get_object_or_404(Category, slug=category_slug)
             posts=Post.objects.filter(category=category).select_related('author','category').prefetch_related('tags')
             serializer=PostSerializer(posts,many=True)
             return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as e :
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#! published post by user
class PublishedPostView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request,post_id):
        try:
            post=Post.objects.get(id=post_id)
            serializer = PublishedPostSerializer(post, data=request.data, partial=True)
            if serializer.is_valid():
                post.published = True
                post.published_at = timezone.now()
                post.save()
                return Response({'response':"your post publish sucessfully"}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        

#! delete post view here..
class DeletePostView(APIView):
    permission_classes=[IsAuthenticated]
    def delete(self,request,post_id):
        try:
            post=get_object_or_404(Post,id=post_id,author=request.user)
            post.delete()
            return Response({'response':'post delete sucessfully'},status=status.HTTP_200_OK)
        except Exception as e:
             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
#! update post view here..
class UpdatePostView(APIView):
    permission_classes=[IsAuthenticated]
    def put(self,request,post_id):
        try:
            post=get_object_or_404(Post,id=post_id,author=request.user)
            serializer=PostSerializer(post,data=request.data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'response':'post update sucessfully'},status=status.HTTP_200_OK)
            else:
                return Response({'response':'post update fail'},serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            


#! likes modle CURD

#! create like view 
class LikeCreateView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request,post_id):
        try:
            post=get_object_or_404(Post,id=post_id)
            if Like.objects.filter(user=request.user, post=post).exists():
                    return Response({'response': 'You have already liked this post'}, status=status.HTTP_400_BAD_REQUEST)
            data={
                'user':request.user.id,
                'post':post.id
            }
            serializer=LikeSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({'response':'post likes sucessfully'},status=status.HTTP_200_OK)
            else:
                return Response({'response':'post likes fail','errors':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
#! delete like view
class LikeDeleteView(APIView):
    permission_classes=[IsAuthenticated]
    def delete(self,request,post_id):
        try:
            like=get_object_or_404(Like,user=request.user,post_id=post_id)
            like.delete()
            return Response({'response': 'Like deleted successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            


#! Comments model curd view...
class CommentCreateView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request,post_id):
        try:
            post=get_object_or_404(Post,id=post_id)
            data=request.data.copy()
            data['post']=post.id
            data['author']=request.user.id
            serializer=CommentSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({'response':'comments post  sucessfully'},status=status.HTTP_200_OK)
            else:
                return Response({'response':'post comments fail','errors':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

#! Comments read view..
class CommentReadView(APIView):
    permission_classes=[AllowAny]
    def get(self,request,post_id):
        try:
            #comments=Comment.objects.filter(post_id=post_id)
            comments = Comment.objects.filter(post_id=post_id).select_related('author', 'post')
            serializers=CommentSerializer(comments,many=True)
            return Response(serializers.data, status=status.HTTP_200_OK)
        except Exception as e:
             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#! comments delete view...
class CommentDeleteView(APIView):
    permission_classes=[IsAuthenticated]
    def delete(self,request,post_id,comment_id):
        try:
            comment=get_object_or_404(Comment,author=request.user,post_id=post_id,id=comment_id)
            comment.delete()
            return Response({'response': 'comments deleted successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


#! comments update view...
class CommentUpdateView(APIView):
    permission_classes=[AllowAny]
    def put(self,request,post_id,comment_id):
        try:
            comment=get_object_or_404(Comment,id=comment_id,post_id=post_id, author=request.user)
            data=request.data.copy()
            data['author']=request.user.id
            data['post']=post_id
            serializer=CommentSerializer(comment,data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({'response':'comments on post update   sucessfully'},status=status.HTTP_200_OK)
            else:
                return Response({'response':' update post comments fail','errors':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

#! Share CRUD goes here ...
class ShareOptionsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, post_id):
        try:
            platforms = ['Facebook', 'Twitter', 'Instagram', 'WhatsApp']
            return Response({'platforms': platforms}, status=status.HTTP_200_OK)
        except Exception as e:
             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class ShareView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        try:
            post = get_object_or_404(Post, id=post_id)
            platform = request.data.get('platform')
            if platform not in ['Facebook', 'Twitter', 'Instagram', 'WhatsApp']:
                return Response({'response': 'Invalid platform'}, status=status.HTTP_400_BAD_REQUEST)
            share_url = generate_share_url(platform, post)
            Share.objects.create(user=request.user, post=post, platform=platform)
            return Response({'response': 'Post shared successfully','share_url': share_url }, status=status.HTTP_200_OK)
        except Exception as e:
             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        





#! bookmark modle CURD

#! create bookmark view 
class BookmarkCreateView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request,post_id):
        try:
            post=get_object_or_404(Post,id=post_id)
            if Bookmark.objects.filter(user=request.user, post=post).exists():
                return Response({'response': 'You have already bookmark this post'}, status=status.HTTP_400_BAD_REQUEST)
            data={'user':request.user.id,'post':post.id}
            serializer=BookmarkSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({'response':'post bookmark sucessfully'},status=status.HTTP_200_OK)
            else:
                return Response({'response':'post bookmark fail','errors':serializer.errors},status=status.HTTP_400_BAD_REQUEST)    
        except Exception as e:
             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#! delete like view
class BookmarkDeleteView(APIView):
    permission_classes=[IsAuthenticated]
    def delete(self,request,post_id):
        try:
            bookmark=get_object_or_404(Bookmark,user=request.user,post_id=post_id)
            bookmark.delete()
            return Response({'response': 'Bookmark deleted successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)