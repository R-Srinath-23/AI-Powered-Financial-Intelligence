from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_view, name='upload'),
    path('transactions/', views.transactions_view, name='transactions'),
    path('pl/', views.pl_view, name='pl'),
    path('review-queue/', views.review_queue_view, name='review_queue'),
    path('variance/', views.variance_view, name='variance'),
    path('chat/', views.chat_view, name='chat'),
    path('chat/message/', views.chat_message_view, name='chat_message'),

]
