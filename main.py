from pygame import *

# создай окно игры
windowWidth = 1000  # Ширина окна игрового поля
windowHeight = 700  # Высота окна игрового поля

window = display.set_mode((windowWidth, windowHeight))
display.set_caption("Ping-pong")

class GameSprite(sprite.Sprite):
    def __init__(self, fileImage, speed, x, y, w, h):
        super().__init__()

        self.w = w
        self.h = h

        if fileImage is None:
            self.image = Surface((self.w, self.h))
            self.image.fill((255,0,0))
        else:
            self.image = transform.scale(image.load(fileImage), (self.w, self.h))


        self.speed = speed
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def __init__(self, fileImage, x, btnUp, btnDown):
        super().__init__(fileImage, 10, x, windowHeight//2-70, 20, 140)

        self.btnUp = btnUp
        self.btnDown = btnDown

    def update(self):
        keys_pressed = key.get_pressed()
        if keys_pressed[self.btnUp] and self.rect.y > 0: self.rect.y -= self.speed
        if keys_pressed[self.btnDown] and self.rect.y < windowHeight-self.h:  self.rect.y += self.speed



player1 = Player(None, 10, K_w, K_s )
player2 = Player(None, windowWidth-20-10, K_UP, K_DOWN)


clock = time.Clock()
FPS = 60

game = True
finish = False
while game:
    #window.blit(background, (0, 0))
    window.fill((50, 200, 200))
    player1.reset()
    player2.reset()


    for e in event.get():
        # обработай событие «клик по кнопке "Закрыть окно"»
        if e.type == QUIT:
            game = False

    player1.update()
    player2.update()

    clock.tick(FPS)
    display.update()