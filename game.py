import arcade
import arcade.gui
import random
import math

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

class Player():
    def __init__(self, sprite):
        self.sprite = sprite
        self.onFloor = True

class Platform():
    def __init__(self, x, width, height):
        self.x = x
        self.width = width
        self.height = height

    def regen(self, x = 0): #change platform size, update location. Optional x argument, used when restarting game
        self.width = random.randint(100, 600)
        self.height = 50 * random.randint(1, 6)
        if x == 0:
            self.x = 1500 + 100 * random.randint(0,5)
        else:
            self.x = x


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.WHITE)
        self.steps = 0
        self.score = float(0)
        self.running = True
        self.ground = 200
        self.yVel = 0
        self.jumping = False
        self.midJump = False
        self.jumpHeight = 35
        self.yVelDecrease = 1.5
        self.platformSpeed = 8
        self.stepsTillLand = 0
        self.jumpRotations = 1
        self.rotationDirection = 1
        self.player = Player(arcade.Sprite("playerSprite.png", center_x= 150, center_y= self.ground + 50, scale = .4))
        #init platforms
        self.platforms = []
        for i in range(7):
            self.platforms.append(Platform(1000 + i * 300 * random.randint(0,4), random.randint(200, 500), 50 * random.randint(1, 6)))
        #init score label
        self.scoreLabel = arcade.gui.UILabel(x = 750, y = 770, text = str(self.score), font_size = 14, text_color = arcade.color.BLACK, width = 100)
        self.scoreManager = arcade.gui.UIManager()
        self.scoreManager.add(self.scoreLabel)

    def on_draw(self):
        arcade.start_render()
        self.clear()
        arcade.draw_rectangle_filled(center_x = 400, center_y = self.ground/2 - 14, width = 800, height = self.ground, color = (20,100,100))
        for platform in self.platforms:
            arcade.draw_rectangle_filled(center_x = platform.x, center_y = self.ground-14 + platform.height/2 , width = platform.width, height = platform.height, color = (150,50,50))
        self.scoreManager.draw()
        self.player.sprite.draw()


    def on_update(self, delta_time):
        if self.running:
            #update score
            self.score += 1   
            self.scoreLabel.text = str(math.trunc(self.score/float(10)))
            #Move player by yVel
            ontoSurface = False #Sets to True if player is about to fall onto a surface (ground or platform)
            if self.yVel < 0 and abs(self.player.sprite.center_y - self.ground) < abs(self.yVel): #if player is about to hit the ground
                self.player.sprite.center_y += -abs(self.player.sprite.center_y - self.ground)
                ontoSurface = True
                # print(f"{self.steps}, landed on ground")

            else: #if player is about to fall onto a platform
                for platform in self.platforms:
                    if platform.x - platform.width/2 -5 < self.player.sprite.center_x < platform.x + platform.width/2:
                        if self.yVel < 0 and abs(self.player.sprite.center_y - (self.ground + platform.height)) < abs(self.yVel):
                            ontoSurface = True
                            # print(f"{self.steps}, landed on plat")
                            self.player.sprite.center_y += -abs(self.player.sprite.center_y - (self.ground + platform.height))
            if not ontoSurface: #else, move by yVel
                self.player.sprite.center_y += self.yVel

            #check if player is on floor
            if self.player.sprite.center_y > self.ground:
                onGround = False
            else:
                onGround = True
            
            #check if player is on platform
            onPlat = False
            for platform in self.platforms:
                if platform.x - platform.width/2 - 5 < self.player.sprite.center_x < platform.x + platform.width/2:
                    if self.yVel <= 0 and self.ground + platform.height >= self.player.sprite.center_y:
                        onPlat = True

            #update yVel
            if onGround or onPlat:
                self.midJump = False
                self.player.onFloor = True
                self.yVel = 0
                self.steps = 0
                if self.jumping:
                    self.jump()
            else:
                self.steps += 1
                self.player.onFloor = False
                self.yVel -= self.yVelDecrease
                if self.midJump:
                    self.player.sprite.angle -= self.rotationDirection * 90 * self.jumpRotations / self.stepsTillLand

            #move platforms
            for platform in self.platforms:
                platform.x -= self.platformSpeed
                if platform.x < -800:
                    platform.regen()
            
            #check death
            for platform in self.platforms:
                if platform.x - platform.width/2 < self.player.sprite.center_x + 17 < platform.x + platform.width/2:
                    if (self.player.sprite.center_y < self.ground + platform.height):
                        self.running = False

    def jump(self):
        found = False
        self.midJump = True
        self.yVel = self.jumpHeight
        #Randomize jump rotation values
        randNum = random.randint(0,100)
        if randNum < 70:
            self.jumpRotations = 1
        elif randNum < 85:
            self.jumpRotations = 2
        elif randNum < 95:
            self.jumpRotations = 3
        else:
            self.jumpRotations = 4
        randNum = random.randint(0,100)
        if randNum < 90:
            self.rotationDirection = 1
        else:
            self.rotationDirection = -1
        #Calculate steps till player will land on ground or platform
        for x in range(24, 65):
            for platform in self.platforms:
                if not found:
                    if platform.x - platform.width/2 - 5 <= (self.player.sprite.center_x + (x * self.platformSpeed)) <= platform.x + platform.width/2:
                        if (self.player.sprite.center_y + (35.75 * x) - (0.75 * (x ** 2))) >= (self.ground + platform.height) >= (self.player.sprite.center_y + (35.75 * (x+1)) - (0.75 * ((x+1) ** 2))):
                            self.stepsTillLand = x
                            # print(f"{self.stepsTillLand} to platform")
                            found = True
                            break                  
                if not found:
                    if (self.player.sprite.center_y + (35.75 * x) - (0.75 * (x ** 2))) >= self.ground >= (self.player.sprite.center_y + (35.75 * (x+1)) - (0.75 * ((x+1) ** 2))):
                        self.stepsTillLand = x
                        # print(f"{self.stepsTillLand} to ground")
                        break
        
    def on_key_press(self, key, key_modifiers):
        if key == arcade.key.SPACE:
            if self.running: #if game is running
                self.jumping = True
                if self.player.onFloor:
                    self.jump()
            else: #if game is over
                print("RESTART")
                for i in range(7):
                    self.platforms[i].regen(1000 + i * 300 * random.randint(0,4)) #regen platforms
                self.score = 0
                self.running = True #restart
                self.player.sprite.angle = 0
                self.jumping = False
                self.midJump = False
    
    def on_key_release(self, key, key_modifier):
        if key == arcade.key.SPACE:
            self.jumping = False
    
def getClosest(curr):
    values = [0,90,180,270,360]
    if curr > 360:
        curr -= 360
    return values[min(range(len(values)), key = lambda i: abs(values[i]-curr))]

window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT)

def main():
    gameView = GameView()
    window.show_view(gameView)
    arcade.run()

main()