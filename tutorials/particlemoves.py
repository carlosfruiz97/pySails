import pygame
from pygame.locals import *
import time
import numpy as np

class Particle(pygame.sprite.Sprite):
    def __init__(self, pos, mass):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)

        self.original_image = pygame.Surface((30,100)).convert_alpha()
        self.original_image.fill((255,0,0))
        self.image = self.original_image

        self.rect = self.image.get_rect()
        self.rect.center = pos

        # Dynamics
        self.angle = 0
        self.x = np.array([pos]).T
        self.v = np.zeros((2,1))
        self.a = np.zeros((2,1))
        self.mass = mass

        self.Forces = {}

        self.Tprev = time.time()

        # Constants
        mu = 0.3
        self.FricCoef = np.array([[mu, 0],[0, mu]])

        # Test
        # self.addForce('Fsail1',[1,0])
        # self.addForce('Fsail2',[0.5,0.5])



    def rotateImage(self,angle):
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        x,y = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def rotate(self,diff):
        self.angle+=diff

    def computeForces(self):
        Ftot = np.zeros((2,1))

        # Sum exterior Forces
        for key in self.Forces:
            Ftot += self.Forces[key]

        # Friction Forces
        Ftot += -np.matmul(self.FricCoef , self.v)

        return Ftot


    def update(self):
        # Get Time difference
        dt = time.time() - self.Tprev
        self.Tprev = time.time()

        # Compute Forces
        F = self.computeForces()

        # Acceleration
        self.a = F / self.mass

        # Velocity
        self.v = self.v + self.a *dt

        # Position and Angle
        self.x = self.x + self.v * dt
        # self.angle = self.angle + self.omega * dt
        self.angle = self.angle % 360
        self.rotateImage(self.angle)
        self.rect.center = [self.x[0,0], self.x[1,0]]

        print(
        'x: {:.3f}, angle: {:.3f}, v={:.3f}, a={:.3f}, F={:.3f}'.format(
            self.x[0,0],self.angle,self.v[0,0],self.a[0,0],F[0,0])
        )


    def addForce(self,newForceName,newForceValue):
        self.Forces[newForceName] = np.array([newForceValue]).T

    def removeForce(self,ForceName):
        del self.Forces[ForceName]
    def removeAllForces(self):
        self.Forces = {}

class App:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.weight, self.height = 640, 400
        self.background_color = (255,255,255)
        self.clock = pygame.time.Clock()
        self.framerate = 60 # frames per second
        self.Ts = 1.0 / self.framerate

        # self.Arrows =

    def on_init(self):
        pygame.init()
        # Surface
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True

        self.ParticleA = Particle( (self.weight*0.5, self.height*0.5), 1 )


    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._running = False

            elif event.key == K_SPACE:
                # self.ParticleA.removeAllForces()
                self.ParticleA.rotate(30)

            # if event.key in [pygame.K_RIGHT, pygame.K_LEFT, pygame.K_DOWN, pygame.K_UP]:
            #     self.addForce()
            # elif event.key == pygame.K_RIGHT:
            #     self.ParticleA.speed[0] = 1
            #     self.ParticleA.applyForce(1)
            # elif event.key == pygame.K_LEFT:
            #     self.ParticleA.speed[0] = -1
            #     self.ParticleA.applyForce(-1)
            # elif event.key == pygame.K_DOWN:
            #     self.ParticleA.speed[1] = 1
            # elif event.key == pygame.K_UP:


    def on_loop(self):
        self.ParticleA.update()

    def on_render(self):
        self._display_surf.fill(self.background_color)
        self.ParticleA.draw(self._display_surf)
        pygame.display.update()

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        if self.on_init() == False:
            self._running = False

        while( self._running ):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
            self.clock.tick(self.framerate)
        self.on_cleanup()

if __name__ == "__main__" :
    theApp = App()
    theApp.on_execute()
