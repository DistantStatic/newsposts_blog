from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Newspost(models.Model):
    newspost_title_text = models.CharField(max_length=200)
    newspost_main_text = models.CharField(max_length=200)
    newspost_photo = models.ImageField(upload_to='post_photos/', null=True, blank=True)
    newspost_audio = models.FileField(upload_to='post_audio/', null=True, blank=True)
    newspost_video = models.FileField(upload_to='post_video/', null=True, blank=True)
    pub_date = models.DateTimeField('date published')
    newspost_author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.newspost_title_text

class Comment(models.Model):
    newspost_parent = models.ForeignKey(Newspost, on_delete=models.CASCADE)
    comment_parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    comment_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    comment_author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    approved_status = models.BooleanField(default=False)

    def __str__(self):
        return self.comment_text

    @property
    def comment_author_name(self):
        """ Intended to easily return author name """
        return self.comment_author.username