import pygame
import random
from mpu6050 import mpu6050
import smbus
import time
import math
import RPi.GPIO as GPIO
import threading
import multiprocessing
from subway_surf import *


buzzer_pin = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(buzzer_pin, GPIO.OUT)

buzzer_pwm = GPIO.PWM(buzzer_pin, 10)
time.sleep(5)


def music(stop_event):
    while not stop_event.is_set():
        for note, duration in zip(melody, durations):
            if stop_event.is_set():  # Check if the game over event is set
                break  # Exit the loop to stop the music immediately
            if duration != 0:
                note_duration = 0.85 / duration
                play_tone(note, note_duration)

            time.sleep(note_duration * 0.7)  # Delay between notes



def initialize_sensor(retries=3, delay=1):
    for attempt in range(retries):
        try:    
            sensor = mpu6050(0x68)
            accelerometer_data = sensor.get_accel_data()
            print("Sensor initialized successfully")
            return sensor
        except OSError as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Failed to initialize sensor after multiple attempts")
                return None
            
def beep_buzzer(frequency, duration):
    buzzer_pwm.ChangeFrequency(frequency)  
    buzzer_pwm.ChangeDutyCycle(50)
    time.sleep(duration)
    buzzer_pwm.ChangeDutyCycle(0)

bus = smbus.SMBus(1)
time.sleep(5) #wait here to avoid 121 IO Error
sensor = initialize_sensor()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

#player settings
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50
PLAYER_COLOR = RED
PLAYER_SPEED = 10

#triangle settings
TRIANGLE_WIDTH = 60
TRIANGLE_HEIGHT = 60
TRIANGLE_HEIGHT_VARIANCE = 20
TRIANGLE_COLOR = RED

TRIANGLE_INITIAL_SPEED = 10
TRIANGLE_MAX_SPEED = 20
TRIANGLE_SPEED_INCREASE = 1
TRIANGLE_INITIAL_AMOUNT = 4
TRIANGLE_MAX_AMOUNT = 7
TRIANGLE_AMOUNT_INCREASE = 1

#wave settings
WAVE_INITIAL_INTERVAL = 800
WAVE_MIN_INTERVAL = 400
WAVE_INTERVAL_DECREASE = 100

#difficulty settings
DIFFICULTY_INCREASE_INTERVAL = 5_000

#events
INCREASE_DIFFICULTY_EVENT = pygame.USEREVENT + 1
INCREMENT_TIMER_EVENT = pygame.USEREVENT + 2

#game states
START_SCREEN = 0
PLAYING = 1
END_SCREEN = 2

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = pygame.image.load('asset/player.png').convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (PLAYER_WIDTH, PLAYER_HEIGHT))
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2
        self.rect.y = SCREEN_HEIGHT - PLAYER_HEIGHT - 10
        self.speed_x = 0

    def update(self):
        # Get roll data from MPU6050
        accel_data = sensor.get_accel_data()
        roll = math.atan2(accel_data['y'], accel_data['z']) * (180.0 / math.pi)

        # Convert roll to speed (adjust sensitivity as needed)
        self.speed_x = roll * 0.5

        self.rect.x += self.speed_x
        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.x > SCREEN_WIDTH - PLAYER_WIDTH:
            self.rect.x = SCREEN_WIDTH - PLAYER_WIDTH


class Triangle(pygame.sprite.Sprite):
    def __init__(self, spawn_pos_x, height_offset=0):
        super().__init__()
        self.image = pygame.Surface([TRIANGLE_WIDTH, TRIANGLE_HEIGHT + height_offset], pygame.SRCALPHA)
        self.original_image = pygame.image.load('asset/obstacle.webp').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = spawn_pos_x
        self.rect.y = -TRIANGLE_HEIGHT
        self.draw_triangle(height_offset)
        self.mask = pygame.mask.from_surface(self.image)

    def draw_triangle(self, height_offset):
        scaled_image = pygame.transform.scale(self.original_image, (TRIANGLE_WIDTH, TRIANGLE_HEIGHT + height_offset))
        self.image.blit(scaled_image, (0, 0))
        self.image = self.image.subsurface(self.image.get_bounding_rect())
        self.rect = self.image.get_rect(topleft=self.rect.topleft)

    def update(self):
        self.rect.y += controller.get_triangle_speed()
        if self.rect.y > SCREEN_HEIGHT:
            self.kill()

    def draw_hitbox(self, screen):
        points = self.mask.outline()
        pygame.draw.lines(screen, RED, True, [(self.rect.x + p[0], self.rect.y + p[1]) for p in points], 2)


class GameController():
    def __init__(self):
        self.max_triangles = TRIANGLE_INITIAL_AMOUNT
        self.triangle_speed = TRIANGLE_INITIAL_SPEED
        self.wave_interval = WAVE_INITIAL_INTERVAL
        self.elapsed_time = 0
        self.is_max_difficulty_list = [False, False, False]

        # (event, time)
        pygame.time.set_timer(pygame.USEREVENT, WAVE_INITIAL_INTERVAL)
        pygame.time.set_timer(INCREASE_DIFFICULTY_EVENT, DIFFICULTY_INCREASE_INTERVAL)
        pygame.time.set_timer(INCREMENT_TIMER_EVENT, 1000)

    def increase_difficulty(self):
        if all(self.is_max_difficulty_list):
            return
        possible_events = [i for (i, x) in enumerate(self.is_max_difficulty_list) if not x]
        random_event = random.choice(possible_events)

        match (random_event):
            case 0:
                self.increase_triangles()
            case 1:
                self.increase_triangle_speed()
            case 2:
                self.decrease_wave_interval()
            case _:
                pass
        print(f"max triangles: {self.max_triangles}  triangle speed: {self.triangle_speed}  wave interval: {self.wave_interval}  isMax: {self.is_max_difficulty_list[0]} {self.is_max_difficulty_list[1]} {self.is_max_difficulty_list[2]}")

    def create_triangles(self):
        triangle_amount = random.randint(1, self.max_triangles)
        triangle_x_positions = []
        for _ in range(triangle_amount):
            height_offset = random.randint(0, 3) * TRIANGLE_HEIGHT_VARIANCE
            spawn_pos_x = random.randint(0, SCREEN_WIDTH - TRIANGLE_WIDTH)

            while any(abs(spawn_pos_x - pos_x) < TRIANGLE_WIDTH for pos_x in triangle_x_positions):
                spawn_pos_x = random.randint(0, SCREEN_WIDTH - TRIANGLE_WIDTH)

            triangle_x_positions.append(spawn_pos_x)
            triangle = Triangle(spawn_pos_x, height_offset)
            all_sprites.add(triangle)
            triangles.add(triangle)

    def increase_triangles(self):
        if self.max_triangles + TRIANGLE_AMOUNT_INCREASE <= TRIANGLE_MAX_AMOUNT:
            self.max_triangles += TRIANGLE_AMOUNT_INCREASE
        else:
            self.max_triangles = TRIANGLE_MAX_AMOUNT
            self.is_max_difficulty_list[0] = True

    def get_triangle_speed(self):
        return self.triangle_speed
    
    def increase_triangle_speed(self):
        if self.triangle_speed + TRIANGLE_SPEED_INCREASE <= TRIANGLE_MAX_SPEED:
            self.triangle_speed += TRIANGLE_SPEED_INCREASE
        else:
            self.triangle_speed = TRIANGLE_MAX_SPEED
            self.is_max_difficulty_list[1] = True

    def decrease_wave_interval(self):
        if self.wave_interval - WAVE_INTERVAL_DECREASE >= WAVE_MIN_INTERVAL:
            self.wave_interval -= WAVE_INTERVAL_DECREASE
        else:
            self.wave_interval = WAVE_MIN_INTERVAL
            self.is_max_difficulty_list[2] = True
        pygame.time.set_timer(pygame.USEREVENT, self.wave_interval)

    def get_elapsed_time(self):
        return self.elapsed_time

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

#setup
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
bg = pygame.image.load("asset/background.jpg").convert_alpha()
bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Caved In")

all_sprites = pygame.sprite.Group()
triangles = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

running = True
controller = GameController()
clock = pygame.time.Clock()
game_state = START_SCREEN

# play_start = multiprocessing.Process(target=play_start_melody)
stop_event = multiprocessing.Event()
music_process = multiprocessing.Process(target=music, args=(stop_event,))

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            # music_process.terminate()
            GPIO.cleanup()
        elif event.type == pygame.KEYDOWN:
            if (game_state == START_SCREEN or game_state == END_SCREEN) and event.key == pygame.K_SPACE: 
                all_sprites.empty()
                triangles.empty()
                player = Player()
                all_sprites.add(player)
                controller = GameController()
                game_state = PLAYING

                # Terminate the old process if it exists
                if music_process.is_alive():
                    music_process.terminate()

                # Create and start a new music process
                stop_event.clear()  # Clear the stop event
                music_process = multiprocessing.Process(target=music, args=(stop_event,))
                music_process.start()
                
        elif event.type == pygame.USEREVENT and game_state == PLAYING:
            controller.create_triangles() 
        elif event.type == INCREASE_DIFFICULTY_EVENT and game_state == PLAYING:
            controller.increase_difficulty()
        elif event.type == INCREMENT_TIMER_EVENT and game_state == PLAYING:
            controller.elapsed_time += 1


    if game_state == PLAYING:
        all_sprites.update()

        # Collision check
        if pygame.sprite.spritecollideany(player, triangles):
            game_state = END_SCREEN
            threading.Thread(target=beep_buzzer, args=(300, 0.5)).start()
            
            # Set the stop_event to stop the music
            stop_event.set()  # This will stop the music abruptly
            music_process.terminate()  # Terminate the music process



    #draw bg
    screen.blit(bg, (0, 0))
    

    if game_state == START_SCREEN:
        draw_text('Press SPACE to Start', pygame.font.Font(None, 48), WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    elif game_state == PLAYING:
        all_sprites.draw(screen)
        draw_text(f'Time Survived: {controller.get_elapsed_time()} seconds', pygame.font.Font(None, 36), WHITE, screen, SCREEN_WIDTH // 2, 30)
    elif game_state == END_SCREEN:
        draw_text('Game Over', pygame.font.Font(None, 48), WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30)
        draw_text(f'Final Time Survived: {controller.get_elapsed_time()} seconds', pygame.font.Font(None, 36), WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30)
        draw_text('Press SPACE to Restart', pygame.font.Font(None, 36), WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80)


    #update display
    pygame.display.flip()

    #limit fps
    clock.tick(60)
pygame.quit()
