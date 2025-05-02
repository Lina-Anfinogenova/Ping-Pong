from pygame import *
from random import randint

# создай окно игры
windowWidth = 1000  # Ширина окна игрового поля
windowHeight = 700  # Высота окна игрового поля

window = display.set_mode((windowWidth, windowHeight))
display.set_caption("Ping-pong")
end = "0"

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
        super().__init__(fileImage, 10, windowWidth//2-30, windowHeight//2-30, 60, 60, colores)

        self.speedX = speedX
        self.speedY = speedY

    def update(self):
        global end
        self.rect.x += self.speedX
        self.rect.y += self.speedY

        if self.rect.y == 0: self.speedY = self.speedY * -1
        if self.rect.y == windowHeight - self.h: self.speedY = self.speedY * -1

        if self.rect.x == 0: 
            end = "winRight"
        if self.rect.x == windowWidth - self.w:
            end = "winLeft"
        
    def withPlayer(self):
        self.speedX = self.speedX * -1

playerLeft = Player(None, 10, (255, 0, 0), K_w, K_s ) #Левый игрок
playerRight = Player(None, windowWidth-20-10, (0, 0, 255), K_UP, K_DOWN) #Правый игрок
#ball = Ball('ball.png', randint(-10, 10),  randint(-10, 10))
ball = Ball('ball.png', 5,  10, None)


clock = time.Clock()
FPS = 60

font.init()
fontEndGame = font.SysFont('Arial', 50)
winRightText = fontEndGame.render('Выиграл правый игрок', True, (255, 0, 0))
winLeftText = fontEndGame.render('Выиграл левый игрок', True, (255, 0, 0))

game = True
finish = False
while game:
    #window.blit(background, (0, 0))
    window.fill((50, 200, 200))
    playerLeft.reset()
    playerRight.reset()
    ball.reset()

    for e in event.get():
        # обработай событие «клик по кнопке "Закрыть окно"»
        if e.type == QUIT:
            game = False

    if not finish:

        if sprite.collide_rect(playerLeft, ball) or sprite.collide_rect(playerRight, ball):
            ball.withPlayer()

        if end == "winRight" or end == "winLeft": finish = True

        playerLeft.update()
        playerRight.update()
        ball.update()
    else:
        if end == "winRight":
            x = (windowWidth - winRightText.get_width()) // 2
            y = (windowHeight - winRightText.get_height()) // 2
            window.blit(winRightText, (x, y))
        if end == "winLeft":
            x = (windowWidth - winLeftText.get_width()) // 2
            y = (windowHeight - winLeftText.get_height()) // 2
            window.blit(winLeftText, (x, y))

    clock.tick(FPS)
    display.update()