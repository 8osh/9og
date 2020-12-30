from django.http import HttpResponse
from django.shortcuts import render, HttpResponse, get_object_or_404, HttpResponseRedirect, redirect, Http404, reverse
from django.views import generic
from django.views.generic import TemplateView, ListView, CreateView
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.text import slugify
from taggit.models import Tag
from .models import Post, Comment, Category
from .forms import PostForm, CommentForm
from django import forms
from django.core.mail import send_mail, BadHeaderError

# Create your views here.

def post_index(request):
    post_list       = Post.objects.filter(status='published')
    categories      = Category.objects.filter()
    paginator       = Paginator(post_list, 30)
    page            = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    context = {
        'posts'         : posts,
        'cats'          : categories,
        'page_obj'      : posts,
    }

    return render(request, 'pages/blog.html', context=context)

def post_detail(request, slug):
    post            = get_object_or_404(Post, slug=slug)
    categories      = Category.objects.filter()
    last_comments   = Comment.objects.select_related('post').filter().order_by('-created_on')[:5]
    common_tags     = Post.tags.most_common()[:15]
    form            = CommentForm(request.POST or None)
    if form.is_valid():
        commenter        = form.save(commit=False)
        commenter.post   = post
        commenter        = commenter.save()
        return HttpResponseRedirect(post.get_absolute_url())

    context = {
        'post'          : post,
        'form'          : form,
        'cats'          : categories,
        'last_comments' : last_comments,
        'common_tags'   : common_tags,
    }
    return render(request, 'pages/content.html', context)

def post_create(request):
    if not request.user.is_authenticated:
        raise Http404()
    
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        post        = form.save(commit=False)
        post.user   = request.user
        post.save()
        messages.success(request, 'Yeni gönderi paylaşıldı!')
        return HttpResponseRedirect(post.get_absolute_url())

    context = {
        'form': form,
    }
    return render(request, 'management/pages/post_form.html', context=context)

def post_update(request, slug):
    if not request.user.is_authenticated:
        raise Http404()
    else:
        post = get_object_or_404(Post, slug=slug)
        if request.user.id == post.user.id:
            form = PostForm(request.POST or None, request.FILES or None, instance=post)
            if form.is_valid():
                form.save()
                messages.success(request, 'Gönderi güncellendi!')
                return HttpResponseRedirect(post.get_absolute_url())
            context = {
                'form': form,
                'post': post,
            }

            return render(request, 'management/pages/post_form.html', context=context)
        else:
            messages.error(request, 'Yetkisiz erişim!')
            return redirect('post:post_index')

def post_delete(request, slug):
    if not request.user.is_authenticated:
        raise Http404()
    else:
        post = get_object_or_404(Post, slug=slug)
        if request.user.id == post.user.id:
            post.delete()
            
            messages.success(request, 'Gönderi silindi!')
            return redirect('post:post_index')
        else:
            messages.error(request, 'Yetkisiz erişim!')
            return redirect('post:post_index')

def CategoryView(request, cats):    
    categories      = Category.objects.filter()
    category_posts  = Post.objects.filter(category=cats.replace('-',' '), status='published')
    common_tags     = Post.tags.most_common()[:15]

    context = {
        'cats_title'    : cats.title().replace('-',' '),
        'category_posts': category_posts,
        'cats'          : categories,
        'common_tags'   : common_tags,
    }
    return render(request, 'pages/blog_categories.html', context=context)

def tagged(request, slug):
    tag             = get_object_or_404(Tag, slug=slug)
    posts           = Post.objects.filter(tags=tag)
    categories      = Category.objects.filter()
    common_tags     = Post.tags.most_common()[:15]
    context = {
        'cats'          : categories,
        'tag'           : tag,
        'tag_posts'     : posts,
        'common_tags'   : common_tags,
    }

    return render(request, 'pages/blog_tags_main.html', context=context)


def hack_index(request):
    post_list       = Post.objects.filter(status='published', category='hack').filter().order_by('-edited_on')
    categories      = Category.objects.filter()
    paginator       = Paginator(post_list, 20)
    page            = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    context = {
        'posts'         : posts,
        'cats'          : categories,
        'page_obj'      : posts,
    }

    return render(request, 'pages/hack.html', context=context)


def tools_index(request):
    post_list       = Post.objects.filter(status='published', category='tools').filter().order_by('-edited_on')
    categories      = Category.objects.filter()
    paginator       = Paginator(post_list, 20)
    page            = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    context = {
        'posts'         : posts,
        'page_obj'      : posts,
    }
    return render(request, 'pages/tools.html', context=context)

def psychology_index(request):
    post_list       = Post.objects.filter(status='published', category='psychology').filter().order_by('-edited_on')
    categories      = Category.objects.filter()
    paginator       = Paginator(post_list, 10)
    page            = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    context = {
        'posts'         : posts,
        'page_obj'      : posts,
    }
    return render(request, 'pages/psychology.html', context=context)

def contact(request):
    if request.method == 'POST':
        message_name    = request.POST['message-name']
        message_email   = request.POST['message-email']
        message         = f"Mail: {request.POST['message-email']} | Mesaj:{request.POST['message']}"

        send_mail(
            message_name,
            message,
            message_email,
            ['beyogluinc@gmail.com'],
        )

        context = {
            'message_name'  : message_name,
        }
        return render(request, 'pages/contact.html', context=context)
    return render(request, 'pages/contact.html')

class SearchResultsView(ListView):
    model           = Post
    template_name   = 'pages/blog_search.html'
    paginate_by     = 10

    def get_queryset(self):
        query       = self.request.GET.get('q')
        global object_list
        object_list = Post.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) |
            Q(user__first_name=query) |
            Q(user__last_name=query),
            status='published'
        )

        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_post"] = object_list
        return context
    
    
    