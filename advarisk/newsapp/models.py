from django.db import models
from advarisk.users.models import User
from django.db.models import JSONField

# Create your models here.
class Keyword(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    keyword = models.CharField(max_length=255)
    last_searched = models.DateTimeField(auto_now=True)
    latest_published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'keyword')

    def __str__(self): 
     return self.keyword
    

class Article(models.Model):
    keyword = models.ForeignKey(Keyword, related_name='articles', on_delete=models.CASCADE)
    articles_list = models.JSONField()  # Store the list of articles

    # def __str__(self):
    #     return self.json_data.get('title', 'No Title')