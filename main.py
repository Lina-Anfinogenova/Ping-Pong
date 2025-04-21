from pygame import *

# создай окно игры
windowWidth = 1000  # Ширина окна игрового поля
windowHeight = 700  # Высота окна игрового поля

window = display.set_mode((windowWidth, windowHeight))
display.set_caption("Ping-pong")

clock = time.Clock()
FPS = 60

game = True
finish = False
while game:
    #window.blit(background, (0, 0))
    window.fill((50, 200, 200))

    for e in event.get():
        # обработай событие «клик по кнопке "Закрыть окно"»
        if e.type == QUIT:
            game = False

    keys_pressed = key.get_pressed()

    clock.tick(FPS)
    display.update()