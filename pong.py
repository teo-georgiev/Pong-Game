# PLAN
# *********************************************************************
# Construct map: 
    # Two players on left and right 
    # Top and bottom walls 
    # Middle dividing line - dashed line 
    # Score for player 1
    # Score for player 2
# Change score based on which player has missed the ball
# Ball disappears on the left and right side 
# Ball bounces off top / bottom walls 
# Ball bounces off players 
# Players can move up and down 
# *********************************************************************

import pygame
import math
import random
import numpy

class Player: 
    def __init__(self, width, height, x_coord, y_coord, score, move_up, move_down):
        self.width = width
        self.height = height
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.score = score
        self.move_up = move_up
        self.move_down = move_down

class Ball: 
    def __init__(self, size, x_coord, y_coord, x_direction, y_direction):
        self.size = size
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.x_direction = x_direction
        self.y_direction = y_direction

class PongGame: 
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        # Display set up
        self.screen_width = 640
        self.screen_height = 480
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.game_font = pygame.font.Font("Brickshapers-eXPx.ttf", 64)
        self.level_font = pygame.font.Font("Brickshapers-eXPx.ttf", 24)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Pong")
        
        #Gameplay variables
        self.colors((5, 30, 0), (45, 230, 0))
        self.velocity = 2.0
        self.progress = 0
        self.level = 1

        # PLAYERS
        self.initialize_players()
        
        # Ball
        self.ball_size = 10
        self.initialize_ball(self.ball_size)
        
        # Sounds 
        self.bounce = "retro-video-game-coin-pickup-38299.mp3"
        self.level_up = "game-start-6104.mp3"
        self.miss = "attack-jingle-sound-effect-jvanko-125083.mp3"
        
        self.main_loop()
    
    def main_loop(self):
        while True: 
            self.draw_screen()
            self.check_events()
            self.players_move(self.p_left, self.screen_height)
            self.players_move(self.p_right, self.screen_height)
            self.now = pygame.time.get_ticks()
            pygame.display.flip()
            self.clock.tick(60)

    def colors(self, bg_color: tuple, main_color: tuple):
        self.bg_color = bg_color
        self.main_color = main_color

    def draw_screen(self): 
        self.screen.fill(self.bg_color)
        self.draw_ball(self.ball, self.screen, self.main_color)
        self.draw_players(self.p_left, self.screen, self.main_color)
        self.draw_players(self.p_right, self.screen, self.main_color)
        self.ball_move(self.ball)
        self.display_scores()
        self.display_level()
        self.draw_dashed_line((self.screen_width/2, 0), (self.screen_width/2, self.screen_height))
    
    def initialize_players(self):
        self.p_left = Player(10, 80, 0, 200, 0, False, False)
        self.p_right = Player(10, 80, self.screen_width - 10, 200, 0, False, False)
    
    def initialize_ball(self, ball_size: int):
        self.ball = Ball(
            ball_size, 
            self.screen_width/2 - ball_size/2,
            self.screen_height/2 - ball_size/2,
            random.choice([-1, 1]), 
            random.choice([-1, 1])
            )
        
    def draw_ball(self, ball: Ball, screen: pygame.Surface, color: tuple):        
        ball = pygame.Rect(
            ball.x_coord, 
            ball.y_coord, 
            ball.size, 
            ball.size
            )
        pygame.draw.rect(screen, color, ball)
    
    def draw_players(self, player: Player, screen: pygame.Surface, color: tuple):
        rect_player = pygame.Rect(
            player.x_coord,
            player.y_coord,
            player.width,
            player.height
            )
        pygame.draw.rect(screen, color, rect_player)
    
    def ball_move(self, ball: Ball):    
        # Restricting the ball's move along the Y axis 
        if ball.y_coord <= 0 or ball.y_coord >= self.screen_height - 10:
            ball.y_direction *= -1
        
        # Score change when ball goes out of the frame along the X axis
        if ball.x_coord <= 0: 
            self.ball_reset()
            self.p_right.score += 1
            self.sound(self.miss)
        elif ball.x_coord >= self.screen_width:
            self.ball_reset()
            self.p_left.score += 1
            self.sound(self.miss)
        
        # Set the ball to bounce from the players
        self.ball_bounce_players(ball)
        
        # Defauly ball movement
        ball.x_coord += self.velocity * ball.x_direction
        ball.y_coord += self.velocity * ball.y_direction
    
    def ball_bounce_players(self, ball: Ball): 
        if (
                (
                ball.x_coord <= (self.p_left.x_coord + self.p_left.width) and 
                self.p_left.y_coord <= ball.y_coord <= ball.y_coord + ball.size <= (self.p_left.y_coord + self.p_left.height)
                ) 
            or
                (
                (ball.x_coord + ball.size) >= self.p_right.x_coord and 
                self.p_right.y_coord <= ball.y_coord <= ball.y_coord + ball.size <= (self.p_right.y_coord + self.p_right.height)
                )
            ): 
            self.sound(self.bounce)
            ball.x_direction *= -1
            self.progress += 1
            self.increse_level(self.progress)
        
    def ball_reset(self): 
        self.initialize_ball(self.ball_size)
        self.draw_ball(self.ball, self.screen, self.main_color)
    
    def increse_level(self, progress: int):
        if progress % 5 == 0 and self.level <= 7: 
            self.velocity += 0.5
            self.level += 1
            self.sound(self.level_up)
        
    def display_scores(self):
        score_left = self.game_font.render(f"{self.p_left.score}", True, self.main_color)
        score_left_rect = score_left.get_rect()
        score_left_rect.right = self.screen_width / 2 - 20
        self.screen.blit(score_left, score_left_rect)
        
        score_right = self.game_font.render(f"{self.p_right.score}", True, self.main_color)
        score_right_rect = score_right.get_rect()
        score_right_rect.left = self.screen_width / 2 + 20
        self.screen.blit(score_right, score_right_rect)
        
    def display_level(self):
        level = self.level_font.render(f"LEVEL {self.level}", True, self.main_color)
        level_rect = level.get_rect()
        level_rect.top = self.screen_height - level.get_height() * 2
        level_rect.right = self.screen_width / 2 + level.get_width() / 2
        self.screen.blit(level, level_rect)
        
    def draw_dashed_line(self, start_post, end_pos, width = 1, dash_length = 5):
        x1, y1 = start_post
        x2, y2 = end_pos
        dl = dash_length
        
        if (x1 == x2): 
            ycoords = [y for y in range(y1, y2, dl if y1 < y2 else -dl)]
            xcoords = [x1] * len(ycoords)
        elif (y1 == y2): 
            xcoords = [x for x in range(x1, x2, dl if x1 < x2 else -dl)]
            ycoords = [y1] * len(xcoords)
        else: 
            a = abs(x2 - x1)
            b = abs(y2 - y1)
            c = round(math.sqrt(a**2 + b**2))
            dx = dl * a / c
            dy = dl * b / c
            
            xcoords = [x for x in numpy.arange(x1, x2, dx if x1 < x2 else -dx)]
            ycoords = [y for y in numpy.arange(y1, y2, dy if y1 < y2 else -dl)]
        
        next_coords = list(zip(xcoords[1::2], ycoords[1::2]))
        last_coords = list(zip(xcoords[0::2], ycoords[0::2]))
        for (x1, y1), (x2, y2) in zip(next_coords, last_coords): 
            start = (round(x1), round(y1))
            end = (round(x2), round(y2))
            pygame.draw.line(self.screen, self.main_color, start, end, width)
    
    def check_events(self):
        for event in pygame.event.get(): 
            if event.type == pygame.KEYDOWN: 
                if event.key == pygame.K_w:
                    self.p_left.move_up = True
                if event.key == pygame.K_s:
                    self.p_left.move_down = True
                
                if event.key == pygame.K_UP:
                    self.p_right.move_up = True
                if event.key == pygame.K_DOWN: 
                    self.p_right.move_down = True
                
                if event.key == pygame.K_r and pygame.key.get_mods() & pygame.KMOD_SHIFT: 
                    self.initialize_players()
                    self.initialize_ball(self.ball_size)
                    
                if event.key == pygame.K_ESCAPE: 
                    exit()
                
            if event.type == pygame.KEYUP: 
                if event.key == pygame.K_w: 
                    self.p_left.move_up = False
                if event.key == pygame.K_s: 
                    self.p_left.move_down = False
                
                if event.key == pygame.K_UP: 
                    self.p_right.move_up = False
                if event.key == pygame.K_DOWN:
                    self.p_right.move_down = False
            
            if event.type == pygame.QUIT: 
                exit()
         
    def players_move(self, player: Player, screen_height: int): 
        player_velocity = 5
        
        if player.move_up: 
            player.y_coord -= player_velocity
            if player.y_coord < 0:
                player.y_coord = 0
        if player.move_down: 
            player.y_coord += player_velocity
            if (player.y_coord + player.height) > screen_height:
                player.y_coord = screen_height - player.height
    
    def sound(self, sound_file): 
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play()
    
PongGame()
