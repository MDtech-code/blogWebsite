from django.urls import path
from . import views

urlpatterns = [
    path('signup/',views.SignupViews.as_view(),name='signup'),
    path('send_verify_email/',views.SendEmailVerificationView.as_view(),name='SendVerifyEmail'),
    path ('verify_email/',views.EmailVerifyViews.as_view(),name='emailVerify'),
    path('login/',views.LoginViews.as_view(),name='login'),
    path('forget_password/',views.ForgetPasswordViews.as_view(),name='forgetPassword'),
    path('logout/',views.LogoutViews.as_view(),name='logout'),
    path('reset_password/',views.ResetPasswordView.as_view(),name='reset_password'),
    path('profile/', views.ProfileRetrieveView.as_view(), name='profile-retrieve'),
    path('profile/create/',views.ProfileCreateView.as_view(), name='profile-create'),
    path('profile/update/',views.ProfileUpdateView.as_view(), name='profile-update'),
    
]
