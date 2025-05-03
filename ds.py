import pygame
import math

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 800, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 20, 100
BALL_SIZE = 15
MAX_PRESS_DURATION = 3000 # Время набора максимальной силы удара, мс
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")

# Шрифты
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 50)

class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = 5

    def move(self, dy):
        self.rect.y += dy
        self.rect.y = max(0, min(self.rect.y, HEIGHT - PADDLE_HEIGHT))

class Ball:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, BALL_SIZE, BALL_SIZE)
        self.is_ready_to_launch = True
        self.launch_side = "left"
        self.dx = 0
        self.dy = 0
        self.offset_y = 0  # Новый атрибут для смещения по Y
        
    def reset(self, side):
        self.is_ready_to_launch = True
        self.launch_side = side
        self.offset_y = 0  # Сбрасываем смещение
        
        if side == "left":
            self.rect.center = (paddle_left.rect.centerx + PADDLE_WIDTH//2 + BALL_SIZE//2, 
                               paddle_left.rect.centery)
        else:
            self.rect.center = (paddle_right.rect.centerx - PADDLE_WIDTH//2 - BALL_SIZE//2,
                               paddle_right.rect.centery)

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
        direction = 1 if paddle.rect.left < WIDTH//2 else -1
        
        speed = math.hypot(ball.dx, ball.dy) * 1.02
        ball.dx = direction * speed * math.cos(angle)
        ball.dy = speed * math.sin(angle)
        
        if direction > 0:
            ball.rect.left = paddle.rect.right
        else:
            ball.rect.right = paddle.rect.left

# Инициализация объектов
paddle_left = Paddle(20, HEIGHT//2 - PADDLE_HEIGHT//2)
paddle_right = Paddle(WIDTH - 40, HEIGHT//2 - PADDLE_HEIGHT//2)
ball = Ball()
ball.reset("left")

# Счет
score_left = 0
score_right = 0
game_over = False

clock = pygame.time.Clock()
space_pressed_time = 0

def reset_game():
    global score_left, score_right, game_over
    score_left = 0
    score_right = 0
    game_over = False
    ball.reset("left")

running = True
while running:
    # Очистка экрана
    screen.fill(BLACK)
    
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

    # Управление ракетками
    keys = pygame.key.get_pressed()
    if not game_over:
        # Левая ракетка
        if keys[pygame.K_w]:
            paddle_left.move(-paddle_left.speed)
        if keys[pygame.K_s]:
            paddle_left.move(paddle_left.speed)
        
        # Правая ракетка
        if keys[pygame.K_UP]:
            paddle_right.move(-paddle_right.speed)
        if keys[pygame.K_DOWN]:
            paddle_right.move(paddle_right.speed)

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
                ball.reset("right")
        elif ball.rect.left > WIDTH:
            score_left += 1
            if score_left >= 11:
                game_over = True
            else:
                ball.reset("left")

    # Отрисовка игровых объектов
    pygame.draw.rect(screen, WHITE, paddle_left.rect)
    pygame.draw.rect(screen, WHITE, paddle_right.rect)
    pygame.draw.ellipse(screen, WHITE, ball.rect)
    pygame.draw.aaline(screen, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT))

    # Отрисовка счета
    score_text = font.render(f"{score_left} : {score_right}", True, WHITE)
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 20))

    # Индикатор силы удара
    if ball.is_ready_to_launch and not game_over:
        power = min((pygame.time.get_ticks() - space_pressed_time) / 1000, 1.0)
        pygame.draw.rect(screen, GREEN, (WIDTH//2 - 50, HEIGHT-20, 100 * power, 10))

    # Экран победы
    if game_over:
        winner_text = font.render("PLAYER LEFT WINS!" if score_left >= 11 else "PLAYER RIGHT WINS!", True, RED)
        screen.blit(winner_text, (WIDTH//2 - winner_text.get_width()//2, HEIGHT//2 - 50))
        restart_text = small_font.render("Press ENTER to restart", True, WHITE)
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 50))

    # Обновление экрана
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()