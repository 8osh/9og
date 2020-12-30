from django.urls import include, path, re_path
from django.conf.urls import url
from .views import *

app_name = 'post'

urlpatterns = [
    path('', post_index, name="post_index"),
    path('hack/', hack_index, name="hack_index" ),
    path('tools/', tools_index, name="tools_index" ),
    path('psychology/', psychology_index, name="psychology_index"),
    path('contact', contact, name="contact"),
    path('search/', SearchResultsView.as_view(),  name="search"),
    path('create/', post_create, name="post_create"),
    path('<slug:slug>/', post_detail, name="post_detail"),
    path('categories/<str:cats>/', CategoryView, name='category'),
    path('<slug:slug>/update/', post_update, name="post_update"),
    path('<slug:slug>/delete/', post_delete, name="post_delete"),
    path('tags/<slug:slug>/', tagged, name="tagged"),
]
