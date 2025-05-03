import pygame
import math

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 1400, 700
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 140
BALL_SIZE = 20
MAX_PRESS_DURATION = 3000 # Время набора максимальной силы удара, мс
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0,   0,   0)
RED =   (255, 0,   0)
GREEN = (0,   255, 0)
BLUE =  (0,   0,   255)

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Пинг-понг")

pygame.display.set_icon(pygame.image.load('ball.png')) # Установка иконки окна

background = pygame.transform.scale(pygame.image.load("Table.png"), (WIDTH, HEIGHT)) # задай фон сцены

# Шрифты
font = pygame.font.SysFont('Arial', 74)
small_font = pygame.font.SysFont('Arial', 50)

class GameSprite(pygame.sprite.Sprite):
    def __init__(self, fileImage=None, speed=0, x=0, y=0, w=0, h=0, colores=(0, 0, 0)):
        super().__init__()

        self.w = w
        self.h = h
        self.colores = colores

        if fileImage is None:
            self.image = pygame.Surface((self.w, self.h))
            self.image.fill(self.colores)
        else:
            self.image = pygame.transform.scale(pygame.image.load(fileImage), (self.w, self.h))

        self.speed = speed
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def reset(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def __init__(self, fileImage, x, colores, btnUp, btnDown):
        super().__init__(fileImage, speed=10, x=x, y=(HEIGHT-PADDLE_HEIGHT)//2, w=PADDLE_WIDTH, h=PADDLE_HEIGHT, colores=colores)

        self.btnUp = btnUp
        self.btnDown = btnDown

    def update(self):
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[self.btnUp] and self.rect.top > 0: self.rect.y -= self.speed
        if keys_pressed[self.btnDown] and self.rect.bottom < HEIGHT:  self.rect.y += self.speed

class Ball(GameSprite):
    def __init__(self, fileImage=None, speedX=0, speedY=0, colores=WHITE):
        super().__init__(fileImage, w=BALL_SIZE, h=BALL_SIZE)
        self.is_ready_to_launch = True
        self.launch_side = "left"
        self.dx = 0
        self.dy = 0
        self.offset_y = 0  # Новый атрибут для смещения по Y
        
    def restart(self, side):
        self.is_ready_to_launch = True
        self.launch_side = side
        self.offset_y = 0  # Сбрасываем смещение
        
        if side == "left":
            self.rect.center = (paddle_left.rect.right + BALL_SIZE//2, paddle_left.rect.centery)
        else:
            self.rect.center = (paddle_right.rect.left - BALL_SIZE//2, paddle_right.rect.centery)

    def move(self):
        if not self.is_ready_to_launch:
            self.rect.x += self.dx
            self.rect.y += self.dy

            if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
                self.dy *= -1

def check_collision(ball, paddle):
    if not ball.is_ready_to_launch and ball.rect.colliderect(paddle.rect):
        hit_position = (ball.rect.centery - paddle.rect.centery) / (PADDLE_HEIGHT / 2)
        hit_position = max(-1, min(hit_position, 1))
        
        angle = hit_position * math.radians(75)
        if paddle.rect.left < WIDTH//2:
            direction = 1
        else:
            direction = -1
        
        speed = math.hypot(ball.dx, ball.dy) * 1.02
        ball.dx = direction * speed * math.cos(angle)
        ball.dy = speed * math.sin(angle)
        
        if direction > 0:
            ball.rect.left = paddle.rect.right
            shoot_right.play()
        else:
            ball.rect.right = paddle.rect.left
            shoot_left.play()

# Инициализация объектов
paddle_left = Player(None, 10, RED, pygame.K_w, pygame.K_s ) #Левый игрок
paddle_right = Player(None, WIDTH-PADDLE_WIDTH-10, BLUE, pygame.K_UP, pygame.K_DOWN) #Правый игрок
ball = Ball('ball.png')
ball.restart("left")

# Счет
score_left = 0
score_right = 0
game_over = False

# Звуки
pygame.mixer.init()
# pygame.mixer.music.load('space.ogg')
# pygame.mixer.music.set_volume(0.5)
# pygame.mixer.music.play(-1)
shoot_left = pygame.mixer.Sound('udar_left.ogg')
#shoot_left.set_volume(0.5)
shoot_right = pygame.mixer.Sound('udar_right.ogg')
#shoot_right.set_volume(0.5)

clock = pygame.time.Clock()
space_pressed_time = 0

def reset_game():
    global score_left, score_right, game_over
    score_left = 0
    score_right = 0
    game_over = False
    ball.restart("left")

running = True
while running:
    # Очистка экрана
    #screen.fill(BLACK)
    screen.blit(background, (0, 0))
    
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        # Обработка НАЖАТИЯ клавиш
        elif event.type == pygame.KEYDOWN:
            # Запуск мяча (только когда готовы к старту)
            if event.key == pygame.K_SPACE and ball.is_ready_to_launch and not game_over:
                space_pressed_time = pygame.time.get_ticks()
                
            # Перезапуск игры (только когда игра окончена)
            if event.key == pygame.K_RETURN and game_over:
                reset_game()
                
        # Обработка отпускания SPACE для удара
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE and ball.is_ready_to_launch and not game_over:
                # Расчет параметров удара
                press_duration = pygame.time.get_ticks() - space_pressed_time
                press_duration = min(press_duration, MAX_PRESS_DURATION)
                speed = 5 + (press_duration / MAX_PRESS_DURATION) * 10
                
                # Определение ракетки и расчет угла
                paddle = paddle_left if ball.launch_side == "left" else paddle_right
                hit_position = (ball.rect.centery - paddle.rect.centery) / (PADDLE_HEIGHT / 2)
                hit_position = max(-1, min(hit_position, 1))
                angle = hit_position * math.radians(60)
                
                # Установка скорости и направления
                direction = 1 if ball.launch_side == "left" else -1
                ball.dx = direction * speed * math.cos(angle)
                ball.dy = speed * math.sin(angle)
                ball.is_ready_to_launch = False

    keys = pygame.key.get_pressed()
    # Управление ракетками
    if not game_over:
        paddle_left.update()
        paddle_right.update()
        
    # Управление позицией мяча на ракетке
    if ball.is_ready_to_launch and not game_over:
        move_step = 3
        if ball.launch_side == "left":
            if keys[pygame.K_a]:
                ball.offset_y = max(-PADDLE_HEIGHT//2 + BALL_SIZE, ball.offset_y - move_step)
            if keys[pygame.K_d]:
                ball.offset_y = min(PADDLE_HEIGHT//2 - BALL_SIZE, ball.offset_y + move_step)
        else:
            if keys[pygame.K_LEFT]:
                ball.offset_y = max(-PADDLE_HEIGHT//2 + BALL_SIZE, ball.offset_y - move_step)
            if keys[pygame.K_RIGHT]:
                ball.offset_y = min(PADDLE_HEIGHT//2 - BALL_SIZE, ball.offset_y + move_step)

    # Обновление позиции мяча при подготовке
    if ball.is_ready_to_launch and not game_over:
        if ball.launch_side == "left":
            paddle = paddle_left
            x_pos = paddle.rect.right + BALL_SIZE//2
        else:
            paddle = paddle_right
            x_pos = paddle.rect.left - BALL_SIZE//2
            
        y_pos = paddle.rect.centery + ball.offset_y
        y_pos = max(paddle.rect.top + BALL_SIZE//2, min(y_pos, paddle.rect.bottom - BALL_SIZE//2))
        ball.rect.center = (x_pos, y_pos)

    # Движение мяча и проверка коллизий
    if not game_over:
        ball.move()
        check_collision(ball, paddle_left)
        check_collision(ball, paddle_right)

    # Проверка голов
    if not game_over and not ball.is_ready_to_launch:
        if ball.rect.right < 0:
            score_right += 1
            if score_right >= 11:
                game_over = True
            else:
                ball.restart("right")
        elif ball.rect.left > WIDTH:
            score_left += 1
            if score_left >= 11:
                game_over = True
            else:
                ball.restart("left")

    # Отрисовка игровых объектов
    paddle_left.reset()
    paddle_right.reset()
    ball.reset()
    #pygame.draw.aaline(screen, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT))

    # Отрисовка счета
    score_text = font.render(f"{score_left} : {score_right}", True, WHITE)
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 20))

    # Индикатор силы удара
    if ball.is_ready_to_launch and not game_over:
        power = min((pygame.time.get_ticks() - space_pressed_time) / MAX_PRESS_DURATION, 1.0)
        pygame.draw.rect(screen, GREEN, (WIDTH//2 - 50, HEIGHT-20, 100 * power, 10))

    # Экран победы
    if game_over:
        winner_text = font.render("Выиграл левый игрок!" if score_left >= 11 else "Выиграл правый игрок!", True, RED)
        screen.blit(winner_text, (WIDTH//2 - winner_text.get_width()//2, HEIGHT//2 - 50))
        restart_text = small_font.render("Нажмите ENTER для перезапуска", True, WHITE)
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 50))

    # Обновление экрана
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()