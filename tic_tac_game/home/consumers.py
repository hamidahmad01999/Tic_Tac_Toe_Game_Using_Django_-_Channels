from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json


class GameRoom(WebsocketConsumer):
    def connect(self):
        from home.models import Game, Box, GameStats
        self.room_name = self.scope['url_route']['kwargs']['room_code']
        self.room_group_name = f"room_{self.room_name}"
        self.game = Game.objects.get(room_code=self.room_name)
        self.boxes = Box.objects.filter(game= self.game)
        self.game_creator= self.game.game_creator
        self.game_opponent= self.game.game_opponent
        self.turn = self.game_creator
        self.user = self.scope['user']
        self.game_stats = GameStats.objects.filter(game=self.game)
        
        # print(self.room_group_name)
        print("Connection established")
        print("Scope is: ", self.scope)
        
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        
        self.accept()
        # as user joined give him previous details and his images
        self.selfJoined()
        if(self.game_opponent):
            self.opponentJoined(self.game_opponent)
            
    # give information related to current game and users status like online/offline
    def getGameStatusData(self):
        from home.models import GameStats
        game_stats = GameStats.objects.filter(game=self.game).first()
        if(self.user.username==self.game_creator):
            game_stats.is_creator_online=True
        else:
            game_stats.is_opponent_online=True  
        game_stats.save()
        return game_stats.is_creator_online,game_stats.is_opponent_online, game_stats.games_creator_won, game_stats.games_opponent_won, game_stats.total_games
    
    # who left the game
    def whoLeaveNow(self):
        from home.models import GameStats
        game_stats = GameStats.objects.filter(game=self.game).first()
        if(self.user.username==self.game_creator):
            game_stats.is_creator_online=False
        else:
            game_stats.is_opponent_online=False 
        game_stats.save()
        return not game_stats.is_creator_online,not game_stats.is_opponent_online  
    
    # if any user join again due to bad internet or reload the page this function will help to load previous states of game and game page
    def selfJoined(self):
        from home.models import Box, Game, Profile
        from django.contrib.auth.models import User
        game = Game.objects.get(room_code=self.room_name)
        self.boxes = Box.objects.filter(game= self.game)
        
        # get creator image and show on play page
        creator_user = User.objects.filter(username=self.game_creator).first()
        creator_profile = Profile.objects.filter(user=creator_user).first()
        creator_image=""
        if creator_profile and creator_profile.image:
            creator_image = creator_profile.image.url
        
        # get opponent image and show on play page
        opponent_image=""
        if self.game_opponent:  #because opponent will join after creator so for creator it's gurantee he will join eralier
            opponent_user = User.objects.filter(username=self.game_opponent).first()
            opponent_profile =Profile.objects.filter(user=opponent_user).first()
            if opponent_profile and opponent_profile.image:
                opponent_image = opponent_profile.image.url 
            
        
        box_data=[]
        for i in range(9):
            box_data.append(self.boxes[i].box_value)
            
        # tell who is online now
        # creator_online, opponent_online = self.howIsOnline()
        creator_online, opponent_online, games_creator_won, games_opponent_won, total_games = self.getGameStatusData()
        print("Creator join: ", creator_online, "Opponent join", opponent_online)
        message = {'message_type':'self_joined','box_data':box_data, 'turn':game.turn, 'creator_image':creator_image, 'opponent_image':opponent_image, 'creator_online':creator_online,
                   'opponent_online':opponent_online}
        
        self.send(text_data=json.dumps({
            'payload':message
        }))
    
    # in the beginning of game we don't know who is opponent but we know who is creator so as opponent join store his information and send to all users
    def opponentJoined(self, opponent_name):
        
        creator_online, opponent_online = self.howIsOnline()
        
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'opponent_joined_notify',
                'message':{
                    'message_type':'opponent',
                    'opponent':'joined',
                    'opponent_username':opponent_name,
                    'creator_online':creator_online,
                    'opponent_online':opponent_online
                }
            }
        )
        
    # this is funciton for above one
    def opponent_joined_notify(self, event):
        self.game_opponent=event['message'].get('opponent_username')
        from home.models import Box, Game, Profile
        from django.contrib.auth.models import User
        game = Game.objects.get(room_code=self.room_name)
        self.boxes = Box.objects.filter(game= self.game)
        
        opponent_user = User.objects.filter(username=self.game_opponent).first()
        opponent_profile = Profile.objects.filter(user=opponent_user).first()
        
        opponent_image=""
        if opponent_profile and opponent_profile.image:
            opponent_image =opponent_profile.image.url
        
        box_data=[]
        for i in range(9):
            box_data.append(self.boxes[i].box_value)
            
        # actually if creator join the server so creator joined will be true 
        # creator_joined, opponent_joined = self.howIsOnline()
        creator_online, opponent_online, games_creator_won, games_opponent_won, total_games  = self.getGameStatusData()
        turn = game.turn
        message = event['message']
        message['box_data']=box_data
        message['turn']=turn
        message['opponent_image']=opponent_image
        message['creator_online'] = creator_online
        message['opponent_online'] = opponent_online
        message['opponent_name'] = opponent_user.first_name
        message['creator_won'] =games_creator_won
        message['opponent_won'] =games_opponent_won
        message['total_games'] = total_games
        message['draw_games'] = total_games - (games_creator_won + games_opponent_won)
        self.send(text_data=json.dumps({
            'payload':message
        }))
    
    # as any uer leave this funciton will call and this funciton will call --> notify_user_disconnected function which will tell all other users that this particular player is offline now
    def disconnect(self, event):
        print(event)
        
        # here it will work in reverse if creator_online True so it means he is actually offline
        creator_offline, opponent_offline = self.whoLeaveNow()
       
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type':'notify_user_disconnected',
                'message':{
                    'message_type':'user_disconnected',
                    'd_username':self.user.username,
                    'creator_offline':creator_offline,
                    'opponent_offline':opponent_offline
                }
                
            }
        )
        
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        print(f"{self.user} disconnected")
        print("Disconnected sucessfully")
        
        
    def notify_user_disconnected(self, event):
        message = event['message']
        
        self.send(text_data=json.dumps({
            'payload':message
        }))
        
    # this funciton will run as user send any update from frontend like on which box he played turn, who win the game whether game is running, draw or anyone won
    def receive(self, text_data):
        data = json.loads(text_data)
        data=data.get("data")
        
        # game is running
        if(data.get("type")=="running"):
            box = self.boxes[int(data.get("index"))]
            box.box_value = data.get("player")
            box.save()
            
        # game is draw or someone win 
        elif(data.get("type")=="over" or data.get("type")=="end" ):
                    
            for i in range(len(self.boxes)):
                box = self.boxes[i]
                box.box_value =""
                box.save()
                
        # increment win of user in his profile and game stats 
        send_game_stats_data = False # whehter sending game stats(how won/draw) it will be only true if we are sending this info
        game_stats={}
        if(data.get("type")=="end"): #someone won
            send_game_stats_data = True  
            if self.user.username==data.get("win_username"): #got username of won player from messaged send from frontend and then update that user's profile and game stats also
                from home.models import Profile
                profile = Profile.objects.filter(user=self.user).first()
                profile.wins=profile.wins+1
                profile.save()
                
            from home.models import GameStats
            Game_stat = GameStats.objects.filter(game=self.game).first()
            if self.user.username==self.game_creator:
                Game_stat.games_creator_won = Game_stat.games_creator_won + 1
            else:
                Game_stat = GameStats.objects.filter(game=self.game).first()
                Game_stat.games_opponent_won = Game_stat.games_opponent_won + 1
            Game_stat.total_games = Game_stat.total_games+1
            Game_stat.save()
        
        # game over so now update game over in game stats
        if(data.get("type")=="over"):
            from home.models import GameStats
            Game_stat = GameStats.objects.filter(game=self.game).first()
            Game_stat.total_games = Game_stat.total_games+1
            Game_stat.save()
            
        game_stats_info =self.getGameStatusData()
        game_stats['creator_won'] = game_stats_info[2]
        game_stats['opponent_won'] = game_stats_info[3]
        game_stats['total_games'] = game_stats_info[4]
        game_stats['draw_games'] = game_stats_info[4] - (game_stats_info[2] + game_stats_info[3])
        
        new_turn=data.get("turn")
        if(not self.game_opponent):
            opponent_exist="no"
        else:
            new_turn=self.changeTurn(data.get("turn"))
            opponent_exist="yes"
        
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type':'run_game', # which function call
                'payload':text_data,    # funciton parameter which it recieves in a dict
                'new_turn':new_turn,
                'opponent':opponent_exist,
                'game_stats_data':send_game_stats_data,
                'game_stats':game_stats
            }
        )

    # it's used to send message during the game to send game states(like who won how many matches), game boxes values any message to send on fronted etc
    def run_game(self, event):
        print("Run game")
        from home.models import Box, Game
        self.boxes = Box.objects.filter(game= self.game)
        box_data=[]
        for i in range(9):
            box_data.append(self.boxes[i].box_value)
        data = event['payload']
        data = json.loads(data)
        
        # adding more values in payload to handle frontend
        data.get('data')["box_data"]=box_data
        data.get('data')["message_type"]="game"
        data.get('data')["opponent"]=event['opponent']
        data.get('data')["turn"]=event['new_turn']
        data.get('data')["game_stats_data"]=event['game_stats_data']
        data.get('data')["game_stats"]=event['game_stats']
        
        self.send(text_data=json.dumps({
            'payload':data['data']
        }))
        
    # it change the turn and store to which player current turn's belong
    def changeTurn(self, old_turn):
        
        from home.models import Game
        game = Game.objects.get(room_code=self.room_name)
        
        if(old_turn == self.game_creator):
        
            turn=self.game_opponent
            game.turn=self.game_opponent
            game.save()
        else:
            turn=self.game_creator
            game.turn=self.game_creator
            game.save()
            
        return game.turn
    