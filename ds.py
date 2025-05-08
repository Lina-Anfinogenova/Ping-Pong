import os
import pygame
import math
import random

# Указываем положение окна в координатах экрана
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (50, 50)

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 1400, 700
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 140
BALL_SIZE = 20
MAX_PRESS_DURATION = 3000 # Время набора максимальной силы удара, мс
MAX_ANGLE_OF_DEVIATION = 60 #Максимальный угол отбивания мяча от ракетки
WINNING_GOAL = 11 #До скольки очков идет игра
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
menu_font = pygame.font.SysFont("Arial", 36)

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
    def __init__(self, fileImage=None, x=0, colores=(255,255,255), btnUp=None, btnDown=None, is_bot=False):
        super().__init__(fileImage, speed=10, x=x, y=(HEIGHT-PADDLE_HEIGHT)//2, w=PADDLE_WIDTH, h=PADDLE_HEIGHT, colores=colores)

        self.btnUp = btnUp
        self.btnDown = btnDown

        # Настройки бота
        self.is_bot = is_bot  # Флаг для определения бота
        self.bot_reaction = 0.8  # Точность реакции бота (0.0-1.0)
        self.bot_error_rate = 20 # Погрешность в предсказании координаты мяча
        self.bot_dead_zone = 5 # Мертвая зона вокруг цели для предотвращения "дерганий" бота
        self.bot_fast_speed_factor = 0.6 # Коэфициент к скорости бота для быстрого движения к цели (если бот еще далеко)
        self.bot_slow_speed_factor = 0.3 # Коэфициент к скорости бота для медленного движения к цели (если бот близко к цели)
        self.bot_speed_change_distance = 20 # Расстояние до цели смены коэфициеента скорости

    def update(self, dy=None):
        if dy != None:
            self.rect.y += dy
            self.rect.y = max(0, min(self.rect.y, HEIGHT - PADDLE_HEIGHT))
        else:
            keys_pressed = pygame.key.get_pressed()
            if keys_pressed[self.btnUp] and self.rect.top > 0: self.rect.y -= self.speed
            if keys_pressed[self.btnDown] and self.rect.bottom < HEIGHT:  self.rect.y += self.speed

    def bot_update(self, ball):
        if self.is_bot:
            # Предсказываем будущую позицию мяча с учетом скорости
            if not ball.is_ready_to_launch and ball.dx > 0:  # Мяч летит в сторону бота
                # Рассчитываем время до столкновения
                time_to_impact = (self.rect.left - ball.rect.right) / ball.dx
                future_y = ball.rect.centery + ball.dy * time_to_impact
                
                # Добавляем случайную погрешность
                future_y += random.randint(-self.bot_error_rate, self.bot_error_rate) * (1 - self.bot_reaction)
                
                # Плавное движение к цели
                target_y = future_y - self.rect.height/2
                target_y = max(0, min(target_y, HEIGHT - PADDLE_HEIGHT))

                # Добавляем мертвую зону 5 пикселей
                if abs(self.rect.centery - target_y) > self.bot_dead_zone:
                    speed_factor = self.bot_fast_speed_factor if abs(self.rect.centery - target_y) > self.bot_speed_change_distance else self.bot_slow_speed_factor
                    if self.rect.centery < target_y:
                        self.update(self.speed * speed_factor)
                    else:
                        self.update(-self.speed * speed_factor)
            else:
                # Возвращаемся в центр, если мяч не летит к боту
                if self.rect.centery < (HEIGHT//2) - self.bot_dead_zone:
                    self.update(self.speed * self.bot_slow_speed_factor)
                elif self.rect.centery > (HEIGHT//2) + self.bot_dead_zone:
                    self.update(-self.speed * self.bot_slow_speed_factor)
        
    def auto_position_ball(self, ball):
        # Случайное смещение мяча для бота
        max_offset = PADDLE_HEIGHT//2 - BALL_SIZE
        ball.offset_y = random.randint(-max_offset, max_offset)
        ball.rect.centery = self.rect.centery + ball.offset_y

class Ball(GameSprite):
    def __init__(self, fileImage=None, speedX=0, speedY=0, colores=WHITE):
        super().__init__(fileImage, w=BALL_SIZE, h=BALL_SIZE)
        self.is_ready_to_launch = True
        self.launch_side = "left" # Cторона запуска мяча
        self.dx = 0
        self.dy = 0
        self.offset_y = 0  # Атрибут для смещения по Y
        self.auto_launch_time = 0 # Случайная задержка для бота
        
    def restart(self, side):
        self.is_ready_to_launch = True
        self.launch_side = side
        self.offset_y = 0  # Сбрасываем смещение
        self.auto_launch_time = pygame.time.get_ticks() + random.randint(1, 6)*500  # Случайная задержка для бота

        # Добавляем автоматическое позиционирование только при сбросе
        if side == "right" and paddle_right.is_bot:
            paddle_right.auto_position_ball(self)  # Вызываем один раз при сбросе
        else:
            if side == "left":
                self.rect.center = (paddle_left.rect.right + BALL_SIZE//2, paddle_left.rect.centery)
            else:
                self.rect.center = (paddle_right.rect.left - BALL_SIZE//2, paddle_right.rect.centery)

    def move(self):
        if not self.is_ready_to_launch:
            self.rect.x += self.dx
            self.rect.y += self.dy

            #удар мяча об стену (верхнюю или нижнюю)
            if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
                hitting_the_wall.play()
                self.dy *= -1

def check_collision(ball, paddle):
    if not ball.is_ready_to_launch and ball.rect.colliderect(paddle.rect):
        hitting_the_racket.play()
        hit_position = (ball.rect.centery - paddle.rect.centery) / (PADDLE_HEIGHT / 2)
        hit_position = max(-1, min(hit_position, 1))
        
        angle = hit_position * math.radians(MAX_ANGLE_OF_DEVIATION)
        if paddle.rect.left < WIDTH//2:
            direction = 1
        else:
            direction = -1
        
        speed = math.hypot(ball.dx, ball.dy) * 1.02 # * 1.02 - коэффициент ускорения при ударе
        ball.dx = direction * speed * math.cos(angle)
        ball.dy = speed * math.sin(angle)
        
        if direction > 0:
            ball.rect.left = paddle.rect.right
        else:
            ball.rect.right = paddle.rect.left

def show_menu():
    screen.fill(BLACK)
    title = font.render("Пинг-Понг", True, WHITE)
    mode1 = menu_font.render("1 - Игра против бота", True, GREEN)
    mode2 = menu_font.render("2 - Два игрока", True, BLUE)
    quit_text = menu_font.render("Q - Выход", True, RED)

    screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
    screen.blit(mode1, (WIDTH//2 - mode1.get_width()//2, 300))
    screen.blit(mode2, (WIDTH//2 - mode2.get_width()//2, 350))
    screen.blit(quit_text, (WIDTH//2 - quit_text.get_width()//2, 400))

    pygame.display.flip()

game_mode=None
menu=True
while menu:
    show_menu()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            menu=False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                game_mode=1
                menu=False
            elif event.key == pygame.K_2:
                game_mode=2
                menu=False
            elif event.key == pygame.K_q:
                pygame.quit()
                menu=False

if game_mode in [1, 2]:
    # Инициализация объектов
    paddle_left = Player(None, 10, RED, pygame.K_w, pygame.K_s ) #Левый игрок

    if game_mode == 1:
        paddle_right = Player(None, WIDTH-PADDLE_WIDTH-10, BLUE, is_bot=True) #Правыый бот
    else:
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
    hitting_the_racket = pygame.mixer.Sound('hitting_the_racket.OGG') #удар мяча об ракетку
    hitting_the_wall = pygame.mixer.Sound('hitting_the_wall.OGG') #удар мяча об стену
    ball_drop = pygame.mixer.Sound('ball_drop.OGG') #падение мяча (гол)
    falling_rackets = pygame.mixer.Sound('falling_rackets.OGG') #бросок ракеток на стол (проигрыш)


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
        screen.blit(background, (0, 0))
        
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False
                
            # Обработка НАЖАТИЯ клавиш
            elif event.type == pygame.KEYDOWN:
                # Запуск мяча (только когда готовы к старту)
                if event.key == pygame.K_SPACE and ball.is_ready_to_launch and not game_over \
                    and ((ball.launch_side == "left" and not paddle_left.is_bot) \
                        or(ball.launch_side == "right" and not paddle_right.is_bot)):
                    space_pressed_time = pygame.time.get_ticks()
                    
                # Перезапуск игры (только когда игра окончена)
                if event.key == pygame.K_RETURN and game_over:
                    reset_game()
                    
            # Обработка отпускания SPACE для удара
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE and ball.is_ready_to_launch and not game_over\
                and ((ball.launch_side == "left" and not paddle_left.is_bot) \
                    or(ball.launch_side == "right" and not paddle_right.is_bot)):
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

        # Автоматический запуск для бота
        if ball.is_ready_to_launch and not game_over \
            and ((ball.launch_side == "left" and paddle_left.is_bot) \
                    or(ball.launch_side == "right" and paddle_right.is_bot)):
            if pygame.time.get_ticks() > ball.auto_launch_time:
                # Случайные параметры удара
                speed = random.uniform(8, 12)
                hit_position = (ball.rect.centery - paddle_right.rect.centery) / (PADDLE_HEIGHT / 2)
                angle = hit_position * math.radians(random.randint(45, 75))
                
                ball.dx = -1 * speed * math.cos(angle)
                ball.dy = speed * math.sin(angle)
                ball.is_ready_to_launch = False

        keys = pygame.key.get_pressed()
        # Управление ракетками
        if not game_over:
            paddle_left.update()
            if paddle_right.is_bot:
                paddle_right.bot_update(ball)
            else:
                paddle_right.update()
            
        # Управление позицией мяча на ракетке
        if ball.is_ready_to_launch and not game_over:
            move_step = 3
            if ball.launch_side == "left":
                if keys[pygame.K_a]:
                    ball.offset_y = max(-PADDLE_HEIGHT//2 + BALL_SIZE, ball.offset_y - move_step)
                if keys[pygame.K_d]:
                    ball.offset_y = min(PADDLE_HEIGHT//2 - BALL_SIZE, ball.offset_y + move_step)
            if ball.launch_side == "right" and not paddle_right.is_bot:
                if keys[pygame.K_LEFT]:
                    ball.offset_y = max(-PADDLE_HEIGHT//2 + BALL_SIZE, ball.offset_y - move_step)
                if keys[pygame.K_RIGHT]:
                    ball.offset_y = min(PADDLE_HEIGHT//2 - BALL_SIZE, ball.offset_y + move_step)

        # Обновление позиции мяча при подготовке (приклеивание мяча к ракетке)
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
                ball_drop.play()
                score_right += 1
                if score_right >= WINNING_GOAL:
                    game_over = True
                    falling_rackets.play()
                else:
                    ball.restart("right")
            elif ball.rect.left > WIDTH:
                ball_drop.play()
                score_left += 1
                if score_left >= WINNING_GOAL:
                    game_over = True
                    falling_rackets.play()
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
            winner_text = font.render("Выиграл левый игрок!" if score_left >= WINNING_GOAL else "Выиграл правый игрок!", True, RED)
            screen.blit(winner_text, (WIDTH//2 - winner_text.get_width()//2, HEIGHT//2 - 50))
            restart_text = small_font.render("Нажмите ENTER для перезапуска", True, WHITE)
            screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 50))

        # Обновление экрана
        pygame.display.flip()
        clock.tick(FPS)