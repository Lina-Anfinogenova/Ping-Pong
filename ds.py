import pygame
import math

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 800, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 20, 100
BALL_SIZE = 15
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")

class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = 5

    def move(self, dy):
        self.rect.y += dy
        # Ограничение движения в пределах экрана
        self.rect.y = max(0, min(self.rect.y, HEIGHT - PADDLE_HEIGHT))

class Ball:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, BALL_SIZE, BALL_SIZE)
        self.reset(side="left")

    def reset(self, side):
        # Начальная скорость в зависимости от стороны
        speed = 5
        if side == "left":
            self.dx = speed
        else:
            self.dx = -speed
        self.dy = 0

    def move(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

        # Отражение от верхней и нижней стенок
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.dy *= -1

def check_collision(ball, paddle):
    if ball.rect.colliderect(paddle.rect):
        # Рассчитываем точку удара относительно центра ракетки
        hit_position = (ball.rect.centery - paddle.rect.centery) / (PADDLE_HEIGHT / 2)
        
        # Ограничиваем значение от -1 до 1
        hit_position = max(-1, min(hit_position, 1))
        
        # Рассчитываем угол отскока (максимум 75 градусов)
        angle = hit_position * math.radians(75)
        
        # Определяем направление отскока
        if paddle.rect.left < WIDTH // 2:  # Левая ракетка
            direction = 1
        else:  # Правая ракетка
            direction = -1
        
        # Вычисляем новую скорость
        speed = math.hypot(ball.dx, ball.dy)
        ball.dx = direction * speed * math.cos(angle)
        ball.dy = speed * math.sin(angle)
        
        # Предотвращаем залипание мяча
        if direction > 0:
            ball.rect.left = paddle.rect.right
        else:
            ball.rect.right = paddle.rect.left

# Создание объектов
paddle_left = Paddle(20, HEIGHT//2 - PADDLE_HEIGHT//2)
paddle_right = Paddle(WIDTH - 40, HEIGHT//2 - PADDLE_HEIGHT//2)
ball = Ball(WIDTH//2 - BALL_SIZE//2, HEIGHT//2 - BALL_SIZE//2)

clock = pygame.time.Clock()

running = True
while running:
    screen.fill(BLACK)
    
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Управление ракетками
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        paddle_left.move(-paddle_left.speed)
    if keys[pygame.K_s]:
        paddle_left.move(paddle_left.speed)
    if keys[pygame.K_UP]:
        paddle_right.move(-paddle_right.speed)
    if keys[pygame.K_DOWN]:
        paddle_right.move(paddle_right.speed)

    # Движение мяча
    ball.move()
    
    # Проверка коллизий
    check_collision(ball, paddle_left)
    check_collision(ball, paddle_right)
    
    # Проверка выхода за пределы экрана
    if ball.rect.left <= 0 or ball.rect.right >= WIDTH:
        ball.reset("left" if ball.rect.left <= 0 else "right")

    # Отрисовка объектов
    pygame.draw.rect(screen, WHITE, paddle_left.rect)
    pygame.draw.rect(screen, WHITE, paddle_right.rect)
    pygame.draw.ellipse(screen, WHITE, ball.rect)
    pygame.draw.aaline(screen, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT))
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()