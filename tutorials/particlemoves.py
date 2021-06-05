import pygame
from pygame.locals import *
import time
import numpy as np
from math import sin, cos, radians, degrees

class Particle(pygame.sprite.Sprite):
    def __init__(self, pos, mass):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)

        # self.original_image = pygame.Surface((30,100)).convert_alpha()
        self.original_image = pygame.image.load("../drawings/Ship1.png").convert_alpha()
        # self.original_image.fill((255,0,0))
        self.image = self.original_image

        self.rect = self.image.get_rect()
        self.rect.center = pos

        # Dynamics
        self.angle = 45
        self.x = np.array([pos]).T
        self.v_world = np.zeros((2,1))
        self.v_boat = np.zeros((2,1))
        self.a_world = np.zeros((2,1))
        self.a_boat = np.zeros((2,1))
        self.mass = mass

        self.Forces = {}

        self.Tprev = time.time()

        # Constants. Respect {x,y}boat
        muX, muY = (0.1, 1)
        self.FricCoef = np.array([[muX, 0],[0, muY]])

        # Test
        self.addForce('Fsail1',[1,0])

        # self.v_world =np.array([[1],[1]])
        # self.addForce('Fsail2',[0.5,0.5])



    def rotateImage(self,angle):
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        x,y = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)

    def draw(self, surface):
        # Update Position:
        H = surface.get_size()[1]
        TranstionMat = np.array([[1, 0, 0],[0, -1, H],[0, 0,1]])
        x_world = np.vstack([self.x,1])
        x_screen = np.matmul(TranstionMat, x_world)

        self.rect.center = [x_screen[0,0], x_screen[1,0]]
        self.rotateImage(self.angle)

        # Draw
        surface.blit(self.image, self.rect)

    def rotate(self,diff):
        self.angle+=diff

    def computeForces(self): # Retrun force is world RF
        Ftot = np.zeros((2,1))

        # Sum exterior Forces
        for key in self.Forces:
            Ftot += self.Forces[key]

        # Friction Forces
        Ffric = -np.matmul(self.FricCoef , self.v_boat)
        RM_inv = np.linalg.inv(self.RotationMatrix(self.angle))
        Ftot += np.matmul(RM_inv, Ffric)

        return Ftot


    def update(self):
        # Get Time difference
        dt = time.time() - self.Tprev
        self.Tprev = time.time()

        # Compute Forces
        F = self.computeForces()

        # Acceleration
        self.a_world = F / self.mass

        # Velocity
        self.v_world = self.v_world + self.a_world *dt

        # Position and Angle
        self.x = self.x + self.v_world * dt
        # self.angle = self.angle + self.omega * dt
        self.angle = self.angle % 360

        self.updateReferenceFrame()

        print(
        'angle: {:.3f}, x: ({:.3f}, {:.3f}) ; v=({:.3f}, {:.3f}), a=({:.3f}, {:.3f}),\
          F=({:.3f}, {:.3f})'.format(
            self.angle, self.x[0,0],self.x[1,0],
            self.v_world[0,0],self.v_world[1,0], self.a_world[0,0],self.a_world[1,0],F[0,0],F[1,0])
        )

    def updateReferenceFrame(self):
        # Rotation Matrix
        RM = self.RotationMatrix(self.angle)
        self.v_boat = np.matmul(RM, self.v_world)
        self.a_boat = np.matmul(RM, self.a_world)


    def RotationMatrix(self,angle):
        angle_Rad = radians(angle)
        return np.array([[cos(angle_Rad), -sin(angle_Rad)],
                   [sin(angle_Rad), cos(angle_Rad)] ])

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
