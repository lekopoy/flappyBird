import pygame as pg
import random as rng

pg.init()

SIZE = (432, 768)

screen = pg.display.set_mode(SIZE, pg.SCALED | pg.RESIZABLE)
clock = pg.time.Clock()

gameIcon = pg.image.load("assets/favicon.ico")
pg.display.set_icon(gameIcon)
pg.display.set_caption("Flappy Bird")

fps = 60
running = True

backgroundDay = pg.transform.scale(
    pg.image.load("assets/sprites/background-day.png"), [SIZE[0], SIZE[1]]
)
backgroundNight = pg.transform.scale(
    pg.image.load("assets/sprites/background-night.png"), [SIZE[0], SIZE[1]]
)

menuImage = pg.transform.scale(
    pg.image.load("assets/sprites/message.png"), [SIZE[0]-18, SIZE[1]-32]
)

baseImage = pg.transform.scale(
    pg.image.load("assets/sprites/base.png"), [SIZE[0], 224]
)

playerImages = [
    pg.transform.scale(pg.image.load("assets/sprites/bluebird-upflap.png"), [68, 48]),
    pg.transform.scale(pg.image.load("assets/sprites/bluebird-midflap.png"), [68, 48]),
    pg.transform.scale(pg.image.load("assets/sprites/bluebird-downflap.png"), [68, 48]),
]

gameOver = pg.transform.scale(
    pg.image.load("assets/sprites/gameover.png"), [384, 84]
)

numbers = [
    pg.image.load("assets/sprites/0.png"),
    pg.image.load("assets/sprites/1.png"),
    pg.image.load("assets/sprites/2.png"),
    pg.image.load("assets/sprites/3.png"),
    pg.image.load("assets/sprites/4.png"),
    pg.image.load("assets/sprites/5.png"),
    pg.image.load("assets/sprites/6.png"),
    pg.image.load("assets/sprites/7.png"),
    pg.image.load("assets/sprites/8.png"),
    pg.image.load("assets/sprites/9.png")
]

dieSound = pg.mixer.Sound("assets/audio/die.ogg")
hitSound = pg.mixer.Sound("assets/audio/hit.ogg")
pointSound = pg.mixer.Sound("assets/audio/point.ogg")
pointSound.set_volume(0.3)
wingSound = pg.mixer.Sound("assets/audio/wing.ogg")

changeAnimation = 10

def scoreRender(extent, y, score):
    if len(str(score)) == 1:
        scoreDigit = pg.transform.scale(numbers[score], extent)
        screen.blit(scoreDigit, [SIZE[0]/2 - extent[0]/2, y])
    elif len(str(score)) == 2:
        scoreDigitOne = pg.transform.scale(numbers[int(str(score)[0])], extent)
        scoreDigitTwo = pg.transform.scale(numbers[int(str(score)[1])], extent)
        screen.blit(scoreDigitOne, [SIZE[0]/2 - extent[0], y])
        screen.blit(scoreDigitTwo, [SIZE[0]/2, y])
    elif len(str(score)) == 3:
        scoreDigitOne = pg.transform.scale(numbers[int(str(score)[0])], extent)
        scoreDigitTwo = pg.transform.scale(numbers[int(str(score)[1])], extent)
        scoreDigitThree = pg.transform.scale(numbers[int(str(score)[2])], extent)
        screen.blit(scoreDigitOne, [SIZE[0]/2 - (extent[0]/2 + extent[0]), y])
        screen.blit(scoreDigitTwo, [SIZE[0]/2 - extent[0]/2, y])
        screen.blit(scoreDigitThree, [SIZE[0]/2 + extent[0]/2, y])

class Game():
    def __init__(self):
        self.plrX = SIZE[0] / 2 - 24
        self.plrY = SIZE[1] / 2
        
        self.vy = 0.1
        self.pipeVelocity = 3
        
        self.rotation = 0
        self.currentImage = 0
        
        self.score = 0
        self.counter = 0
        
        self.backgroundSpeed = 2
        self.dayX = 0
        self.nightX = SIZE[0]
        
        self.groundSpeed = 3
        self.ground1 = 0
        self.ground2 = SIZE[0]
        
        self.menu = True
        self.alive = False
        self.dead = False
        
        self.pipes = []

    def inputs(self, key):
        if (key == pg.K_SPACE or key == 1 or key == 2 or key == 3) and self.menu:
            self.alive = True
            self.menu = False
            self.move()
        elif (key == pg.K_SPACE or key == 1 or key == 2 or key == 3) and self.alive and self.plrY > 15:
            self.move()
        elif (key == pg.K_SPACE or key == 1 or key == 2 or key == 3) and self.dead:
            global game
            game = restart(game)
    
    def move(self):
        wingSound.play()
        self.vy = -6
        self.rotation = 40
        
    def backgroundLogic(self):
        self.dayX -= self.backgroundSpeed
        self.nightX -= self.backgroundSpeed
        if self.dayX <= 0 - SIZE[0]:
            self.dayX = SIZE[0]
        elif self.nightX <= 0 - SIZE[0]:
            self.nightX = SIZE[0]
        self.ground1 -= self.groundSpeed
        self.ground2 -= self.groundSpeed
        if self.ground1 <= 0 - SIZE[0]:
            self.ground1 = SIZE[0]
        elif self.ground2 <= 0 - SIZE[0]:
            self.ground2 = SIZE[0]
    
    def logic(self):
        self.backgroundLogic()
        
        if self.alive:
            self.gameLogic()
        elif self.dead:
            self.endLogic()

    def gameLogic(self):
        if self.score == 999:
            self.alive = False
            self.dead = True
            dieSound.play()
            
        if self.plrY + 24 >= SIZE[1] - 180:
            self.alive = False
            self.dead = True
            dieSound.play()
        
        self.pipeVelocity = self.score * 3/20 if self.score >= 20 else 3
        self.groundSpeed = self.pipeVelocity if self.pipeVelocity%3 == 0 else 3
        
        self.counter += 1
        self.vy += 0.2
        self.rotation -= 1 if self.rotation >= -40 else 0

        for pipe in self.pipes:
            self.score = pipe.move(self.score, self.plrX)
            if not pipe.x <= self.plrX + 34 <= pipe.x + 78:
                continue
            if pipe.y - 90 <= self.plrY + 24 <= pipe.y + 90:
                continue
                
            hitSound.play()
            
            self.alive = False
            self.dead = True
            
            dieSound.play()

        if self.counter%changeAnimation == 0:
            if self.vy > 0:
                self.currentImage = 0
            else:
                if self.currentImage < 2:
                    self.currentImage += 1
                else:
                    self.currentImage = 0

        if self.counter%90 == 0:
            newPipe = Pipe()
            self.pipes.append(newPipe)
            
            
        self.plrY += self.vy
        
    def endLogic(self):
        self.vy += 0.3 if self.vy <= 12 else 0
        self.rotation -= 0.8 if self.rotation >= -40 else 0
        self.plrY += self.vy if self.plrY <= 800 else 0
    
    def draw(self):
        screen.blit(backgroundDay, (self.dayX, 0))
        screen.blit(backgroundDay, (self.nightX, 0))

        if self.menu:
            screen.blit(menuImage, [9,16])
            return

        if self.alive:
            for pipe in self.pipes:
                pipe.draw()
                
            scoreRender((24, 36), 4, self.score)

        screen.blit(baseImage, (self.ground1, SIZE[1] - 180))
        screen.blit(baseImage, (self.ground2, SIZE[1] - 180))

        rotatedPlayer = pg.transform.rotate(playerImages[self.currentImage], self.rotation)
        screen.blit(rotatedPlayer, (self.plrX, self.plrY))
        
        if self.dead:
            screen.blit(gameOver, (24,4))
            
            scoreRender((48, 72), 128, self.score)
                
                
class Pipe():
    def __init__(self):
        self.x = SIZE[0] + 20
        self.y = rng.randrange(200,460)
        
        self.vx = game.pipeVelocity
        self.completed = False
        
        self.image = pg.transform.scale(pg.image.load("assets/sprites/pipe-green.png"), [78, 480]) if rng.randrange(1,3) == 1 else pg.transform.scale(pg.image.load("assets/sprites/pipe-red.png"), [78, 480])
        self.imageFlipped = pg.transform.flip(self.image, False, True)
        
    def move(self, score, plrX):
        self.x -= self.vx
        if not self.x < plrX:
            return score
        
        if not self.completed:
            self.completed = True
            score += 1
            pointSound.play()
        
        if not self.x <= -78:
            return score
        
        game.pipes.pop(game.pipes.index(self))
        return score
    
    def draw(self):
        screen.blit(self.image, (self.x, self.y + 90))
        screen.blit(self.imageFlipped, (self.x, self.y - 480 - 90))


def restart(game):
    game = None
    game = Game()
    return game


game = Game()


while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.KEYDOWN:
            game.inputs(event.key)
        elif event.type == pg.MOUSEBUTTONDOWN:
            game.inputs(event.button)

    game.logic()

    game.draw()

    pg.display.flip()
    clock.tick(fps)
    
pg.quit()