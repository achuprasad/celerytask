from django.urls import path
from ecomapp import views as chat_views
from . import views
from django.contrib.auth.decorators import login_required
urlpatterns = [
    path('register',views.RegisterView.as_view()),
    path('users',views.ListView.as_view()),
    path('login',views.CustomLoginView.as_view()),
    path('logout',views.LogoutView.as_view()),
    path('categories',views.CreateCategory.as_view()),
    
    path('password/reset/', views.PasswordResetRequestView.as_view()),
    path('password/verify/',views.OTPVerificationView.as_view()),
    # path('password/change/', views.PasswordChangeView.as_view()),
    # path('products',views.ItemsViews.as_view()),
    # path('items/<int:item_id>/', views.EachItemsView.as_view()),
    #chat
    #    path('', views.lobby),
    path('',views.LoginTemView.as_view(),name="log_template"),
     path('regsiter-temp/', views.UserRegisterView.as_view(), name='register'),
    path('home/',views.HomeView.as_view(),name="home-view"),
    # path("chat", chat_views.chatPage, name="chat-page"),
    path('logouttemp',chat_views.logout_view,name='logout'),

    # path("chat", chat_views.chatPage, name="chat-page"),
    path('chat_list/', views.chat_list, name='chat_list'),
    


   
]
