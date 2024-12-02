from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from home.models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import shortuuid
import os

# home page for user 
@login_required
def home(request):
    try:
        if request.method=="POST":
            username= request.POST.get('username')
            room_code= request.POST.get('room_code')
            option = request.POST.get('option')
            
            boxes=[]
            if option=="1": # one if user have room code it means he is an opponent
                game = Game.objects.filter(room_code=room_code).first()
                
                if game is None:    # check whether game exists to provided room code or not
                    messages.success(request, "Room code not found")
                    return redirect('/')
                
                if game.is_over:    # if game over then also don't need to redirect to play page
                    messages.success(request, "Game is over")
                    return redirect('/')
                game.game_opponent=username
                game.save()
                return redirect(f'/play/{room_code}?username={username}')
            else:
                
                # if user is the one who created game
                game = Game.objects.create(game_creator=username, room_code=room_code, turn = username)
                
                # created GameStats to store stats related to this game and nine boxes to store value of each box in game
                game_stats = GameStats.objects.create(game=game)
                for i in range(9):
                    box = Box.objects.create(game=game,box_number=i)
                    boxes.append(box)
                return redirect(f'/play/{room_code}?username={username}')
        
        top_profiles = Profile.objects.order_by('-points')
        user = request.user
        first_name = user.first_name
        username = user.username
        profile = Profile.objects.filter(user=user).first()
        
        print(first_name, username, profile)
        context = {'first_name':first_name, 'username':username, 'profile':profile, 'top_profiles':top_profiles}
        return render(request, "pages/home.html", context)
    except Exception as e:
        print(e)
        return HttpResponse("Internal server error")
    
# create a unique room id 
@login_required
def create_room_id(request):
    try:
        room_code = shortuuid.uuid()
        return JsonResponse({'room_code':room_code})
    except Exception as e:
        return HttpResponse(False)

from django.conf import settings
@login_required
def upload_image(request):
    if request.method=="POST":
        file = request.FILES['image']
        extract = os.path.splitext(file.name)[1]
        unique_name = f"{request.user.username}{extract}"
        file.name=unique_name
        profile = Profile.objects.filter(user=request.user).first()
        
        if profile.image and profile.image.url:
            old_image = profile.image.url[7:]
        
        # old_image=old_image.replace('/','\\')
            if old_image.startswith(settings.MEDIA_URL.lstrip('/')):
                old_image = old_image[len(settings.MEDIA_URL.lstrip('/')):]
            full_path = os.path.join(settings.MEDIA_ROOT, old_image.lstrip('/'))
        
            if(old_image is not None and os.path.isfile(full_path)):
                os.remove(full_path)
            
        profile.image = file
        profile.save()
        
        return redirect("/")
    
    return redirect("/")

@login_required
def play(request, room_code):
    try:
        game = Game.objects.get(room_code=room_code)
        username = request.GET.get('username')
        
        if(game.game_opponent is not None and username !=game.game_creator and username !=game.game_opponent):
            return HttpResponse("Trying to access wrong page\nLink isn't valid")
        else:
            # updating total matches of player
            profile = Profile.objects.filter(user=request.user).first()
            profile.total_matches = profile.total_matches + 1
            profile.save()
            game_symbol =""
            if(username==game.game_creator):
                game_symbol="X"
            else:
                game_symbol="Y"
            
            
            context = {'username':username,'game_creator_fullname':game.game_creator ,'room_code':room_code,  'game':game, "game_symbol":game_symbol}
            
            return render(request, "pages/play.html", context)
    except Game.DoesNotExist:
        return render(request, "pages/play.html", context)


def register(request):
    try:
        if request.method=="POST":
            username = request.POST.get('username')
            name = request.POST.get('name')
            password = request.POST.get('password')

            user = User.objects.filter(username=username).first()
            if(user):
                messages.error(request, "This username isn't available")
                # next_url = request.POST.get('next', '/')
                # redirect(next_url)
                return redirect(request.path)

            user = User(username=username, first_name=name)

            user.set_password(password)
            user.save()
            print(username, name, password)
            messages.success(request, "User Registered Sucessfully!")
            return redirect(request.path) 

        return render(request, "pages/register.html")
    except:
        return HttpResponse("Internal server error")

    
def login_page(request):
    try:
        if request.method == "POST":
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = User.objects.filter(username=username).first()
            if(not user):
                messages.error(request, "Wrong credentials")
                return redirect(request.path) 

            if(user.check_password(password)):
                login(request,user)
                return redirect("/")
            else:
                messages.error(request, "Wrong credentials")
                return redirect(request.path) 
            
        return render(request, "pages/login.html") 
    except Exception as e:
        return HttpResponse("Internal Server Error.")
    
    
def call_logout(request):
    try:
        logout(request)
        return redirect('/accounts/register')
    except Exception as e:
        print(e)
        return HttpResponse("Internal Server Error.")
    

@login_required
def profile_page(request, id):
    try:
        user = User.objects.filter(id=id).first()
        if(not user):
            return redirect('/')
        profile = Profile.objects.filter(user=user).first()
        
        return render(request, "pages/profile.html", {"user": user, "profile":profile})
    except Exception as e:
        print(e)
        return HttpResponse("Internal Server Error.")