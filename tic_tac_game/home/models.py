from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

class Game(models.Model):
    room_code = models.CharField(max_length=100, unique=True)
    game_creator = models.CharField(max_length=100)
    game_opponent = models.CharField(max_length=100, null=True, blank=True)
    is_over = models.BooleanField(default=False)
    turn = models.CharField(max_length=100, null=True, blank=True)

class GameStats(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    games_creator_won = models.IntegerField(default=0)
    games_opponent_won = models.IntegerField(default=0)
    total_games = models.IntegerField(default=0)
    is_creator_online = models.BooleanField(default=False)
    is_opponent_online = models.BooleanField(default=False)

class Box(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='boxes')
    box_number = models.IntegerField(blank=False, null=False)
    box_value = models.CharField(max_length=1, default="",null=True, blank=True)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    image = models.ImageField(verbose_name="user_image", blank=True, null=True, upload_to="profile/")
    wins = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    losts = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    total_matches = models.IntegerField(default=0)
    rank = models.IntegerField()
    
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        count = User.objects.all().count() + 1
        Profile.objects.create(user=instance, rank=count)
        

