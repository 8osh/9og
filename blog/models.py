from django.db import models
from ckeditor.fields import RichTextField
from datetime import datetime
from django.urls import reverse
from django.utils.text import slugify
from django.conf import settings
from taggit.managers import TaggableManager
from django.utils import timezone

# Create your models here.


class AutoDateTimeField(models.DateTimeField):
    def pre_save(self, model_instance, add):
        return timezone.now()


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True,
                            verbose_name="Kategori")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("post:post_index")

    def save(self, *args, **kwargs):
        return super(Category, self).save(*args, **kwargs)


class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Beklemede'),
        ('published', 'Yayında'),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, verbose_name='Yazar', related_name="user")
    title = models.CharField(max_length=120, verbose_name="Blog Başlığı")
    category = models.CharField(max_length=255, verbose_name="Kategori Adı")
    content = RichTextField(verbose_name="İçerik")
    created_on = models.DateTimeField(
        default=timezone.now, verbose_name="Oluşturma Tarihi")
    edited_on = AutoDateTimeField(
        default=timezone.now, blank=True, verbose_name="Düzenlenme Tarihi")
    thumbnail = models.ImageField(
        null=True, blank=True, verbose_name="Blog Resmi")
    slug = models.SlugField(
        unique=True, verbose_name="Adres", editable=False, max_length=150, null=True)
    tags = TaggableManager()
    status = models.CharField(max_length=10,
                              choices=STATUS_CHOICES,
                              default='published',
                              verbose_name="Durum"
                              )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("post:post_detail", kwargs={"slug": self.slug})

    def get_create_url(self):
        return reverse("post:post_create")

    def get_update_url(self):
        return reverse("post:post_update", kwargs={"slug": self.slug})

    def get_delete_url(self):
        return reverse("post:post_delete", kwargs={"slug": self.slug})

    def get_unique_slug(self):
        slug = slugify(self.title.replace('ı', 'i'))
        unique_slug = slug
        counter = 1
        while Post.objects.filter(slug=unique_slug).exists():
            unique_slug = '{}--{}'.format(slug, counter)
            counter += 1
        return unique_slug

    def save(self, *args, **kwargs):
        # if not self.slug: # alt satırı bir blok içeri al açtığında
        self.slug = self.get_unique_slug()
        return super(Post, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-created_on']

class Comment(models.Model):
    STATUS_CHOICES = (
       ('draft', 'Draft'),
       ('published', 'Published'),
    )
    post        = models.ForeignKey('blog.Post', on_delete=models.CASCADE, related_name="comments")
    name        = models.CharField(max_length=100, verbose_name="İsim")
    email       = models.EmailField(verbose_name="Email", max_length=254)
    content     = models.TextField(verbose_name="Yorum")
    created_on  = models.DateTimeField(auto_now_add=True, verbose_name="Yorum Tarihi")
    status = models.CharField(max_length=10,
                              choices=STATUS_CHOICES,
                              default='published',
                              verbose_name= "Durum",
                              )
    
    def __str__(self):
        return f"{self.content}, | Konu: {self.post}, Yazan: {self.name}"
