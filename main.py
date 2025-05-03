from pygame import *
from random import randint
import math

# создай окно игры
windowWidth = 1400  # Ширина окна игрового поля
windowHeight = 700  # Высота окна игрового поля

window = display.set_mode((windowWidth, windowHeight))
display.set_caption("Ping-pong")
# задай фон сцены
background = transform.scale(image.load("Table.png"), (windowWidth, windowHeight))

class GameSprite(sprite.Sprite):
    def __init__(self, fileImage, speed, x, y, w, h, colores):
        super().__init__()

        self.w = w
        self.h = h
        self.colores = colores

        if fileImage is None:
            self.image = Surface((self.w, self.h))
            self.image.fill(self.colores)
        else:
            self.image = transform.scale(image.load(fileImage), (self.w, self.h))


        self.speed = speed
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def __init__(self, fileImage, x, colores, btnUp, btnDown):
        super().__init__(fileImage, 10, x, windowHeight//2-70, 20, 140, colores)

        self.btnUp = btnUp
        self.btnDown = btnDown

    def update(self):
        keys_pressed = key.get_pressed()
        if keys_pressed[self.btnUp] and self.rect.y > 0: self.rect.y -= self.speed
        if keys_pressed[self.btnDown] and self.rect.y < windowHeight-self.h:  self.rect.y += self.speed

class Ball(GameSprite):
    def __init__(self, fileImage, speedX, speedY, colores):
        self.size = 30
        super().__init__(fileImage, 10, (windowWidth-self.size)//2, (windowHeight-self.size)//2, self.size, self.size, colores)

        self.speedX = speedX
        self.speedY = speedY

        self.out = "None"

    def update(self):
        self.rect.x += self.speedX
        self.rect.y += self.speedY

        # Отражение от верхней и нижней стенок
        if self.rect.top <= 0 or self.rect.bottom >= windowHeight: self.speedY *= -1

        # Пропуск мяча ракеткой
        if self.rect.x <= 0: 
            self.out = "winRight"
        if self.rect.x >= windowWidth - self.w:
            self.out = "winLeft"
        
    def withPlayer(self, player: Player):
        # Рассчитываем точку удара относительно центра ракетки
        hit_position = (self.rect.centery - player.rect.centery) / (player.h / 2)
        
        # Ограничиваем значение от -1 до 1
        hit_position = max(-1, min(hit_position, 1))

        # Рассчитываем угол отскока (максимум 75 градусов)
        angle = hit_position * math.radians(75)
        
        # Определяем направление отскока
        if player.rect.left < windowWidth // 2:  # Левая ракетка
            direction = 1
        else:  # Правая ракетка
            direction = -1

        # Вычисляем новую скорость
        speed = math.hypot(ball.speedX, ball.speedY)
        self.speedX = round(direction * speed * math.cos(angle))
        self.speedY = round(speed * math.sin(angle))
        
        # Предотвращаем залипание мяча
        if direction > 0:
            self.rect.left = player.rect.right
        else:
            self.rect.right = player.rect.left

        #self.speedX = self.speedX * -1

def gameStart():
    ball.speedX = randint(-10, 10)
    if ball.speedX == 0: ball.speedX = 1
    ball.speedY = randint(-10, 10)
    ball.rect.x = (windowWidth - ball.size)//2
    ball.rect.y = (windowHeight - ball.size)//2
    ball.out = "None"

playerLeft = Player(None, 10, (255, 0, 0), K_w, K_s ) #Левый игрок
playerRight = Player(None, windowWidth-20-10, (0, 0, 255), K_UP, K_DOWN) #Правый игрок
ball = Ball('ball.png', 0,  0, None)


clock = time.Clock()
FPS = 60

font.init()
fontEndGame = font.SysFont('Arial', 50)
winRightText = fontEndGame.render('Выиграл правый игрок', True, (255, 0, 0))
winLeftText = fontEndGame.render('Выиграл левый игрок', True, (255, 0, 0))

fontCount = font.SysFont('Arial', 20, bold=True, italic=True)

countLeft = 0
countRight = 0
game = True
finish = True
while game:
    window.blit(background, (0, 0))
    #window.fill((50, 200, 200))
    playerLeft.reset()
    playerRight.reset()
    ball.reset()

    # Отображение счета игры
    countRightText = fontCount.render('Счет: ' + str(countRight), True, (255, 100, 0))
    window.blit(countRightText, (windowWidth-countRightText.get_width()-20, 30))
    countLeftText = fontCount.render('Счет: ' + str(countLeft), True, (255, 100, 0))
    window.blit(countLeftText, (20, 30))

    # #Координаты и параметры мяча
    # text = "x=" + str(ball.rect.x) +"; y=" + str(ball.rect.y) + "; speed = (" + str(ball.speedX) + "; " + str(ball.speedY) + "), out=" + ball.out
    # ballText = fontCount.render(text, True, (255, 100, 0))
    # window.blit(ballText, (20, windowHeight - 30))

    for e in event.get():
        # обработай событие «клик по кнопке "Закрыть окно"»
        if e.type == QUIT:
            game = False

    if not finish:

        if sprite.collide_rect(playerLeft, ball): ball.withPlayer(playerLeft)
        if sprite.collide_rect(playerRight, ball): ball.withPlayer(playerRight)
            

        if ball.out == "winRight":
            countRight += 1
            gameStart()
        if ball.out == "winLeft":
            countLeft += 1
            gameStart()

        if countLeft >= 6 or countRight >= 6: finish = True

        playerLeft.update()
        playerRight.update()
        ball.update()
    else:
        if countRight >= 6:
            x = (windowWidth - winRightText.get_width()) // 2
            y = (windowHeight - winRightText.get_height()) // 2
            window.blit(winRightText, (x, y))
        if countLeft >= 6:
            x = (windowWidth - winLeftText.get_width()) // 2
            y = (windowHeight - winLeftText.get_height()) // 2
            window.blit(winLeftText, (x, y))

        keys_pressed = key.get_pressed()
        if keys_pressed[K_SPACE]: 
            gameStart()
            countLeft = 0
            countRight = 0
            finish = False

    clock.tick(FPS)
    display.update()