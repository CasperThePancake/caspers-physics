import pygame
from numpy import sin, cos, pi, sqrt, array
from numpy.linalg import norm as npnorm


# PyGame init
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial" , 18 , bold = True)
frameRate = 60
pygame.display.set_caption("Casper's Physics Simulation")
running = True

# Initial variables
camX = 0
camY = 0
camZoom = 1
GRAVITY = -9.81
GROUND_SPEED = 0.1
SUBSTEPS = 20
test = 0

# Helpful functions
def diagonal_line_vector(x1, y1, x2, y2, x3, y3, x4, y4):
    """
    Computes the vector of a line through the top-right corner (x2, y2) of a rectangle
    that is at 45 degrees to both the top and right edges.
    
    Args:
        x1, y1: Coordinates of the top-left corner.
        x2, y2: Coordinates of the top-right corner.
        x3, y3: Coordinates of the bottom-right corner.
        x4, y4: Coordinates of the bottom-left corner.
        
    Returns:
        numpy.ndarray: A unit vector in the direction of the desired diagonal.
    """
    # Top edge vector
    top_vector = array([x2 - x1, y2 - y1])
    # Right edge vector
    right_vector = array([x3 - x2, y3 - y2])
    
    # Normalize the vectors
    top_unit = top_vector / npnorm(top_vector)
    right_unit = right_vector / npnorm(right_vector)
    
    # Diagonal vector (sum of normalized vectors)
    diagonal = top_unit + right_unit
    diagonal_unit = diagonal / npnorm(diagonal)
    
    return diagonal_unit
def split_string_to_list(input_string):
    """
    Splits a string at colons (:), then further splits each resulting part at commas (,),
    returning a list of lists.

    Args:
        input_string (str): The string to be split.

    Returns:
        list: A list of lists after splitting by colons and commas.
    """
    # Split the string by colons
    colon_parts = input_string.split(":")
    
    # Split each colon-separated part by commas and build the list of lists
    result = [part.split(",") for part in colon_parts]

    return result
def update_fps():
    fps = str(int(clock.get_fps()))
    fps_text = font.render(fps + " FPS", 1, pygame.Color("black"))
    
    # Create a surface for the background (white)
    text_width, text_height = fps_text.get_size()
    background = pygame.Surface((text_width + 10, text_height + 10))  # Add padding around text
    background.fill(pygame.Color("white"))
    
    # Position the text on the background surface
    background.blit(fps_text, (5, 5))  # Add some padding from the edges
    
    return background
def norm(vector):
    #Only for 2D vectors, returns their norm
    return sqrt(vector[0]**2 + vector[1]**2)

def normalize_angle(angle):
    # Use modulo to bring the angle within the range -2π to 2π
    angle = angle % (2 * pi)
    # If the angle is negative, shift it to the range 0 to 2π
    if angle < 0:
        angle += 2 * pi
    return angle

def circleOnLine(x1, y1, x2, y2, xB, yB, r):
    # Vector from point 1 to point 2
    dx, dy = x2 - x1, y2 - y1
    # Vector from point 1 to the circle's center
    fx, fy = xB - x1, yB - y1

    # Project the circle center onto the line segment, clamping to [0, 1]
    t = max(0, min(1, (fx * dx + fy * dy) / (dx * dx + dy * dy)))

    # Closest point on the line segment to the circle's center
    cx, cy = x1 + t * dx, y1 + t * dy

    # Squared distance from the circle's center to the closest point
    dist_sq = (cx - xB) ** 2 + (cy - yB) ** 2

    # Compare with squared radius to avoid unnecessary sqrt
    return dist_sq <= r * r

# Classes
class Rectangle:
    def __init__(self, x, y, width, height, angle, color="black",bounciness=0.5, gravity=False):
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._color = color
        self._angle = normalize_angle(angle * (pi / 180)) #Make radians
        self._gravity = gravity
        self._bounciness = bounciness
        self._aX = 0
        self._aY = 0
        self._vX = 0
        self._vY = 0
        self._maxlength = sqrt( (self._width / 2)**2 + (self._height / 2)**2 )
        self._onGround = False
        #Define corner polygons for rendering and collision (no recalculation necessary)
        self._polygon1 = (self._x,self._y)
        self._polygon2 = (self._x + self._width * cos(self._angle), self._y - self._width * sin(self._angle))
        self._polygon3 = (self._x - self._height * sin(self._angle) + self._width * cos(self._angle), self._y - self._height * cos(self._angle) - self._width * sin(self._angle))
        self._polygon4 = (self._x - self._height * sin(self._angle), self._y - self._height * cos(self._angle))
        self._center = ((self._polygon1[0]+self._polygon2[0]+self._polygon3[0]+self._polygon4[0])/4 , (self._polygon1[1]+self._polygon2[1]+self._polygon3[1]+self._polygon4[1])/4)
    def draw(self):
        if 0 == 1: #ADD PROPER NON-RENDER CHECK FOR OPTIMIZATION
            return

        screenPolygon1 = (screen.get_width() / 2 - (camX - self._polygon1[0]) , screen.get_height() / 2 - (self._polygon1[1] - camY))
        screenPolygon2 = (screen.get_width() / 2 - (camX - self._polygon2[0]) , screen.get_height() / 2 - (self._polygon2[1] - camY))
        screenPolygon3 = (screen.get_width() / 2 - (camX - self._polygon3[0]) , screen.get_height() / 2 - (self._polygon3[1] - camY))
        screenPolygon4 = (screen.get_width() / 2 - (camX - self._polygon4[0]) , screen.get_height() / 2 - (self._polygon4[1] - camY))
        pygame.draw.polygon(screen,self._color,[screenPolygon1,screenPolygon2,screenPolygon3,screenPolygon4])

    def update(self):
        if self._gravity and not self._onGround:
            self._aY = GRAVITY / (frameRate * SUBSTEPS)
        elif self._onGround:
            self._aY = 0
        # Apply acceleration
        self._vY += self._aY
        self._vX += self._aX
        # Apply speed
        self._x += self._vX / SUBSTEPS
        self._y += self._vY / SUBSTEPS

class Ball:
    def __init__(self, x, y, radius, mass=1, color="black", gravity=True):
        self._x = x
        self._y = y
        self._radius = radius
        self._color = color
        self._gravity = gravity
        self._aX = 0
        self._aY = 0
        self._vX = 0
        self._vY = 0
        self._eaX = 0
        self._eaY = 0
        self._mass = mass
        self._onGround = False
        self._ground = None
        self._lastCollision = None
    def draw(self):
        if (camX - self._x - self._radius > screen.get_width() / 2) or (self._x - camX > screen.get_width() / 2) or (self._y - camY - self._radius > screen.get_height() / 2) or (camY - self._y > screen.get_height() / 2):
            return
        pygame.draw.circle(screen,self._color,((screen.get_width() / 2) - (camX - self._x), (screen.get_height() / 2) - (self._y - camY)),self._radius)

    def update(self):
        self._aX = 0
        self._aY = 0
        #Check if still on ground
        if self._onGround:
            if self._ground._angle == 0: #GROUND = TOP
                if not circleOnLine(self._ground._polygon1[0],self._ground._polygon1[1],self._ground._polygon2[0],self._ground._polygon2[1],self._x,self._y,self._radius):
                    self._onGround = False
                    self._ground = None
            if self._ground._angle == pi/2: #GROUND = LEFT
                if not circleOnLine(self._ground._polygon1[0],self._ground._polygon1[1],self._ground._polygon4[0],self._ground._polygon4[1],self._x,self._y,self._radius):
                    self._onGround = False
                    self._ground = None
            if self._ground._angle == pi: #GROUND = BOTTOM
                if not circleOnLine(self._ground._polygon4[0],self._ground._polygon4[1],self._ground._polygon3[0],self._ground._polygon3[1],self._x,self._y,self._radius):
                    self._onGround = False
                    self._ground = None
            if self._ground._angle == 3*pi/2: #GROUND = RIGHT
                if not circleOnLine(self._ground._polygon2[0],self._ground._polygon2[1],self._ground._polygon3[0],self._ground._polygon3[1],self._x,self._y,self._radius):
                    self._onGround = False
                    self._ground = None
        #Apply gravity
        if self._gravity and not self._onGround and not fly:
            self._aY += GRAVITY / (frameRate * SUBSTEPS)
        #Apply exerted acceleration, if any, and reset
        self._aX += self._eaX
        self._aY += self._eaY
        self._eaX = 0
        self._eaY = 0
        #If on ground, no downward acceleration
        if self._onGround and self._aY < 0:
            self._aY = 0
        if self._onGround and self._aY > 0:
            self._onGround = False
            self._ground = None
        # Apply acceleration
        self._vY += self._aY
        self._vX += self._aX
        # Apply speed
        self._x += self._vX / SUBSTEPS
        self._y += self._vY / SUBSTEPS
    
    def checkCollision(self,other):
        # Find out which types
        polygon1 = other._polygon1
        polygon2 = other._polygon2
        polygon3 = other._polygon3
        polygon4 = other._polygon4

        top = circleOnLine(polygon1[0],polygon1[1],polygon2[0],polygon2[1],self._x,self._y,self._radius)
        right = circleOnLine(polygon2[0],polygon2[1],polygon3[0],polygon3[1],self._x,self._y,self._radius)
        bottom = circleOnLine(polygon3[0],polygon3[1],polygon4[0],polygon4[1],self._x,self._y,self._radius)
        left = circleOnLine(polygon4[0],polygon4[1],polygon1[0],polygon1[1],self._x,self._y,self._radius)

        self._lastCollision = other

        #ONLY BOTTOM
        if bottom and not top and not right and not left: #Polygon 3 and 4
            #Mirror the speed vector over the line vector using projections
            lineVector = (polygon4[0]-polygon3[0],polygon4[1]-polygon3[1])
            speedVector = (self._vX,self._vY)
            mirroredVector = (2 * lineVector[0] * ( speedVector[0] * lineVector[0] + speedVector[1] * lineVector[1] ) / (lineVector[0]**2 + lineVector[1]**2) - speedVector[0] , 2 * lineVector[1] * ( speedVector[0] * lineVector[0] + speedVector[1] * lineVector[1] ) / (lineVector[0]**2 + lineVector[1]**2) - speedVector[1])
            #Update speeds accordingly
            self._vX = other._bounciness * mirroredVector[0]
            self._vY = other._bounciness * mirroredVector[1]
            #Get perp coordinates for snapping
            normalVector = (polygon4[1]-polygon3[1],polygon3[0]-polygon4[0])
            if normalVector[0] == 0:
                perpSideX = self._x
                perpSideY = ((polygon4[1] - polygon3[1]) / (polygon4[0] - polygon3[0])) * (perpSideX - polygon3[0]) + polygon3[1]
            elif normalVector[1] == 0:
                perpSideY = self._y
                perpSideX = (perpSideY - polygon3[1]) * (polygon4[0] - polygon3[0]) / (polygon4[1] - polygon3[1]) + polygon3[0]
            else:
                perpSideX = (self._y - polygon3[1] - (normalVector[1] / normalVector[0]) * self._x + ((polygon4[1] - polygon3[1]) / (polygon4[0] - polygon3[0])) * polygon3[0]) / ( ((polygon4[1] - polygon3[1]) / (polygon4[0] - polygon3[0])) - normalVector[1] / normalVector[0] )
                perpSideY = ((polygon4[1] - polygon3[1]) / (polygon4[0] - polygon3[0])) * (perpSideX - polygon3[0]) + polygon3[1]
            
            #Snap to edge
            perpVector = (self._x - perpSideX,self._y - perpSideY)
            snapVector = (perpVector / norm(perpVector)) * self._radius

            self._x = perpSideX + snapVector[0]
            self._y = perpSideY + snapVector[1]
            #Ground check
            if other._angle == pi and self._vY < GROUND_SPEED:
                self._vY = 0
                self._onGround = True
                self._ground = other

        # ONLY TOP
        if top and not right and not left and not bottom:
            #Mirror the speed vector over the line vector using projections
            lineVector = (polygon1[0]-polygon2[0],polygon1[1]-polygon2[1])
            speedVector = (self._vX,self._vY)
            mirroredVector = (2 * lineVector[0] * ( speedVector[0] * lineVector[0] + speedVector[1] * lineVector[1] ) / (lineVector[0]**2 + lineVector[1]**2) - speedVector[0] , 2 * lineVector[1] * ( speedVector[0] * lineVector[0] + speedVector[1] * lineVector[1] ) / (lineVector[0]**2 + lineVector[1]**2) - speedVector[1])
            #Update speeds accordingly
            self._vX = other._bounciness * mirroredVector[0]
            self._vY = other._bounciness * mirroredVector[1]
            #Get perp coordinates for snapping
            normalVector = (polygon2[1]-polygon1[1],polygon1[0]-polygon2[0])
            if normalVector[0] == 0:
                perpSideX = self._x
                perpSideY = ((polygon2[1] - polygon1[1]) / (polygon2[0] - polygon1[0])) * (perpSideX - polygon1[0]) + polygon1[1]
            elif normalVector[1] == 0:
                perpSideY = self._y
                perpSideX = (perpSideY - polygon1[1]) * (polygon2[0] - polygon1[0]) / (polygon2[1] - polygon1[1]) + polygon1[0]
            else:
                perpSideX = (self._y - polygon1[1] - (normalVector[1] / normalVector[0]) * self._x + ((polygon2[1] - polygon1[1]) / (polygon2[0] - polygon1[0])) * polygon1[0]) / ( ((polygon2[1] - polygon1[1]) / (polygon2[0] - polygon1[0])) - normalVector[1] / normalVector[0] )
                perpSideY = ((polygon2[1] - polygon1[1]) / (polygon2[0] - polygon1[0])) * (perpSideX - polygon1[0]) + polygon1[1]
            
            #Snap to edge
            perpVector = (self._x - perpSideX,self._y - perpSideY)
            snapVector = (perpVector / norm(perpVector)) * self._radius

            self._x = perpSideX + snapVector[0]
            self._y = perpSideY + snapVector[1]
            #Ground check
            if other._angle == 0 and self._vY < GROUND_SPEED:
                self._vY = 0
                self._onGround = True
                self._ground = other

        # ONLY LEFT
        if left and not right and not top and not bottom:
            #Mirror the speed vector over the line vector using projections
            lineVector = (polygon1[0]-polygon4[0],polygon1[1]-polygon4[1])
            speedVector = (self._vX,self._vY)
            mirroredVector = (2 * lineVector[0] * ( speedVector[0] * lineVector[0] + speedVector[1] * lineVector[1] ) / (lineVector[0]**2 + lineVector[1]**2) - speedVector[0] , 2 * lineVector[1] * ( speedVector[0] * lineVector[0] + speedVector[1] * lineVector[1] ) / (lineVector[0]**2 + lineVector[1]**2) - speedVector[1])
            #Update speeds accordingly
            self._vX = other._bounciness * mirroredVector[0]
            self._vY = other._bounciness * mirroredVector[1]
            #Get perp coordinates for snapping
            normalVector = (polygon4[1]-polygon1[1],polygon1[0]-polygon4[0])
            if normalVector[0] == 0:
                perpSideX = self._x
                perpSideY = ((polygon4[1] - polygon1[1]) / (polygon4[0] - polygon1[0])) * (perpSideX - polygon1[0]) + polygon1[1]
            elif normalVector[1] == 0:
                perpSideY = self._y
                perpSideX = (perpSideY - polygon1[1]) * (polygon4[0] - polygon1[0]) / (polygon4[1] - polygon1[1]) + polygon1[0]
            else:
                perpSideX = (self._y - polygon1[1] - (normalVector[1] / normalVector[0]) * self._x + ((polygon4[1] - polygon1[1]) / (polygon4[0] - polygon1[0])) * polygon1[0]) / ( ((polygon4[1] - polygon1[1]) / (polygon4[0] - polygon1[0])) - normalVector[1] / normalVector[0] )
                perpSideY = ((polygon4[1] - polygon1[1]) / (polygon4[0] - polygon1[0])) * (perpSideX - polygon1[0]) + polygon1[1]
            
            #Snap to edge
            perpVector = (self._x - perpSideX,self._y - perpSideY)
            snapVector = (perpVector / norm(perpVector)) * self._radius

            self._x = perpSideX + snapVector[0]
            self._y = perpSideY + snapVector[1]
            #Ground check
            if other._angle == pi/2 and self._vY < GROUND_SPEED:
                self._vY = 0
                self._onGround = True
                self._ground = other
        
        # ONLY RIGHT
        if right and not left and not top and not bottom:
            #Mirror the speed vector over the line vector using projections
            lineVector = (polygon2[0]-polygon3[0],polygon2[1]-polygon3[1])
            speedVector = (self._vX,self._vY)
            mirroredVector = (2 * lineVector[0] * ( speedVector[0] * lineVector[0] + speedVector[1] * lineVector[1] ) / (lineVector[0]**2 + lineVector[1]**2) - speedVector[0] , 2 * lineVector[1] * ( speedVector[0] * lineVector[0] + speedVector[1] * lineVector[1] ) / (lineVector[0]**2 + lineVector[1]**2) - speedVector[1])
            #Update speeds accordingly
            self._vX = other._bounciness * mirroredVector[0]
            self._vY = other._bounciness * mirroredVector[1]
            #Get perp coordinates for snapping
            normalVector = (polygon3[1]-polygon2[1],polygon2[0]-polygon3[0])
            if normalVector[0] == 0:
                perpSideX = self._x
                perpSideY = ((polygon3[1] - polygon2[1]) / (polygon3[0] - polygon2[0])) * (perpSideX - polygon2[0]) + polygon2[1]
            elif normalVector[1] == 0:
                perpSideY = self._y
                perpSideX = (perpSideY - polygon2[1]) * (polygon3[0] - polygon2[0]) / (polygon3[1] - polygon2[1]) + polygon2[0]
            else:
                perpSideX = (self._y - polygon2[1] - (normalVector[1] / normalVector[0]) * self._x + ((polygon3[1] - polygon2[1]) / (polygon3[0] - polygon2[0])) * polygon2[0]) / ( ((polygon3[1] - polygon2[1]) / (polygon3[0] - polygon2[0])) - normalVector[1] / normalVector[0] )
                perpSideY = ((polygon3[1] - polygon2[1]) / (polygon3[0] - polygon2[0])) * (perpSideX - polygon2[0]) + polygon2[1]
            
            #Snap to edge
            perpVector = (self._x - perpSideX,self._y - perpSideY)
            snapVector = (perpVector / norm(perpVector)) * self._radius

            self._x = perpSideX + snapVector[0]
            self._y = perpSideY + snapVector[1]
            #Ground check
            if other._angle == 3*pi/2 and self._vY < GROUND_SPEED:
                self._vY = 0
                self._onGround = True
                self._ground = other
        
        # TOP-RIGHT CORNER
        if top and right and not bottom and not left:
            #Mirror the speed vector over the line vector using projections
            lineVector = diagonal_line_vector(polygon1[0],polygon1[1],polygon2[0],polygon2[1],polygon3[0],polygon3[1],polygon4[0],polygon4[1])
            speedVector = (self._vX,self._vY)
            mirroredVector = (2 * lineVector[0] * ( speedVector[0] * lineVector[0] + speedVector[1] * lineVector[1] ) / (lineVector[0]**2 + lineVector[1]**2) - speedVector[0] , 2 * lineVector[1] * ( speedVector[0] * lineVector[0] + speedVector[1] * lineVector[1] ) / (lineVector[0]**2 + lineVector[1]**2) - speedVector[1])
            #Update speeds accordingly
            self._vX = other._bounciness * mirroredVector[0]
            self._vY = other._bounciness * mirroredVector[1]
            #Get perp coordinates for snapping
            perpSideX = polygon2[0]
            perpSideY = polygon2[1]
            
            #Snap to edge
            perpVector = (self._x - perpSideX,self._y - perpSideY)
            snapVector = (perpVector / norm(perpVector)) * self._radius

            self._x = perpSideX + snapVector[0]
            self._y = perpSideY + snapVector[1]
        
        # BOTTOM-RIGHT CORNER
        if bottom and right and not top and not left:
            #Mirror the speed vector over the line vector using projections
            lineVector = diagonal_line_vector(polygon4[0],polygon4[1],polygon3[0],polygon3[1],polygon2[0],polygon2[1],polygon1[0],polygon1[1])
            speedVector = (self._vX,self._vY)
            mirroredVector = (2 * lineVector[0] * ( speedVector[0] * lineVector[0] + speedVector[1] * lineVector[1] ) / (lineVector[0]**2 + lineVector[1]**2) - speedVector[0] , 2 * lineVector[1] * ( speedVector[0] * lineVector[0] + speedVector[1] * lineVector[1] ) / (lineVector[0]**2 + lineVector[1]**2) - speedVector[1])
            #Update speeds accordingly
            self._vX = other._bounciness * mirroredVector[0]
            self._vY = other._bounciness * mirroredVector[1]
            #Get perp coordinates for snapping
            perpSideX = polygon3[0]
            perpSideY = polygon3[1]
            
            #Snap to edge
            perpVector = (self._x - perpSideX,self._y - perpSideY)
            snapVector = (perpVector / norm(perpVector)) * self._radius

            self._x = perpSideX + snapVector[0]
            self._y = perpSideY + snapVector[1]
        
        # BOTTOM-LEFT CORNER
        if bottom and left and not top and not right:
            #Mirror the speed vector over the line vector using projections
            lineVector = diagonal_line_vector(polygon3[0],polygon3[1],polygon4[0],polygon4[1],polygon1[0],polygon1[1],polygon2[0],polygon2[1])
            speedVector = (self._vX,self._vY)
            mirroredVector = (2 * lineVector[0] * ( speedVector[0] * lineVector[0] + speedVector[1] * lineVector[1] ) / (lineVector[0]**2 + lineVector[1]**2) - speedVector[0] , 2 * lineVector[1] * ( speedVector[0] * lineVector[0] + speedVector[1] * lineVector[1] ) / (lineVector[0]**2 + lineVector[1]**2) - speedVector[1])
            #Update speeds accordingly
            self._vX = other._bounciness * mirroredVector[0]
            self._vY = other._bounciness * mirroredVector[1]
            #Get perp coordinates for snapping
            perpSideX = polygon4[0]
            perpSideY = polygon4[1]
            
            #Snap to edge
            perpVector = (self._x - perpSideX,self._y - perpSideY)
            snapVector = (perpVector / norm(perpVector)) * self._radius

            self._x = perpSideX + snapVector[0]
            self._y = perpSideY + snapVector[1]

        # TOP-LEFT CORNER
        if top and left and not bottom and not right:
            #Mirror the speed vector over the line vector using projections
            lineVector = diagonal_line_vector(polygon2[0],polygon2[1],polygon1[0],polygon1[1],polygon4[0],polygon4[1],polygon3[0],polygon3[1])
            speedVector = (self._vX,self._vY)
            mirroredVector = (2 * lineVector[0] * ( speedVector[0] * lineVector[0] + speedVector[1] * lineVector[1] ) / (lineVector[0]**2 + lineVector[1]**2) - speedVector[0] , 2 * lineVector[1] * ( speedVector[0] * lineVector[0] + speedVector[1] * lineVector[1] ) / (lineVector[0]**2 + lineVector[1]**2) - speedVector[1])
            #Update speeds accordingly
            self._vX = other._bounciness * mirroredVector[0]
            self._vY = other._bounciness * mirroredVector[1]
            #Get perp coordinates for snapping
            perpSideX = polygon1[0]
            perpSideY = polygon1[1]
            
            #Snap to edge
            perpVector = (self._x - perpSideX,self._y - perpSideY)
            snapVector = (perpVector / norm(perpVector)) * self._radius

            self._x = perpSideX + snapVector[0]
            self._y = perpSideY + snapVector[1]

    def exertForce(self,forceX,forceY):
        self._eaX += forceX / self._mass
        self._eaY += forceY / self._mass


def fps_counter():
    fps = str(int(clock.get_fps()))
    fps_t = font.render(fps , 1, pygame.Color("RED"))
    screen.blit(fps_t,(0,0))

def detect_collisions(objects):
    for i in objects:
        if isinstance(i,Ball):
            for j in objects:
                if isinstance(j,Rectangle):
                    if sqrt((j._center[1]- i._y)**2 + (j._center[0] - i._x)**2) < j._maxlength + i._radius and j != i._ground:
                        i.checkCollision(j)
    return

# Initiate objects
scene = []
testBall1 = Ball(0, 200, 10, 2, "red", True)
scene.append(testBall1)

# Editor
editWidth = 20
editHeight = 20
editAngle = 0
editing = False
fly = False
loadCode = "-99999.0,0.0,199998.0,50.0,0.0,black,0.85:102.50000000000279,-4.155677000013611,197,20,5.883185307179586,black,0.85:280.5000000000028,70.854432299998639,197,20,5.6831853071795875,black,0.85:443.5000000000028,182.8443229999864,197,20,6.0663706143591805,black,0.85:633.9999999999812,224.84432299998457,197,20,5.766370614359181,black,0.85:803.9999999999812,321.84432299998457,197,20,5.9495559215387885,black,0.85:989.5000000000158,386.844322999965,197,20,0.24955592153876438,black,0.85:1176.500000000016,339.844322999965,197,20,1.215926535897772,black,0.85:1244.0000000000823,158.84432299996433,197,20,0.9159265358977677,black,0.85:1314.499999999965,507.84432299999503,197,20,5.8991118430773355,black,0.85:1063.499999999965,741.844322999995,197,20,0.39911184307725733,black,0.85:1340.9803470314178,796.3675158350004,197,20,5.782297150256831,black,0.85:1079.9803470314178,873.3675158350004,197,20,3.5822971502567995,black,0.85:1466.480347031334,1007.8675158349417,197,20,2.982297150256791,black,0.85:1721.480347031334,1130.3675158351402,197,20,2.982297150256791,black,0.85:993.4803470313341,1191.867515835202,197,20,0.48229715025675546,black,0.85:759.4803470313341,1313.3675158352357,197,20,0.48229715025675546,black,0.85:539.9803470312804,1424.3675158352357,197,20,0.48229715025675546,black,0.85:338.98034703127473,1610.3675158354395,455,20,0.48229715025675546,black,0.85:101.5978819145273,1222.8475614197498,455,20,5.26548245743632,black,0.85:180.5978819145273,1197.8475614197498,344,20,5.26548245743632,black,0.85:365.5978819145273,1506.8475614197498,218,20,0.4486677646157489,black,0.85:-174.40211808547065,1314.8475614196707,374,20,0.6318530717952484,black,0.85:-170.40211808547065,1449.8475614196707,374,20,0.6318530717952484,black,0.85:191.59788191452935,1216.8475614196707,374,20,0.615038378975065,black,0.85:-417.40211808547065,1170.85475614196707,374,20,5.398223686154736,black,0.85:-410.40211808547065,1022.8475614196707,374,20,5.398223686154736,black,0.85:-109.90211808546633,803.8475614197871,374,20,5.398223686154736,black,0.85:-382.9021180854663,877.8475614197871,374,20,5.398223686154736,black,0.85:-289.9021180854663,816.8475614197871,374,20,5.398223686154736,black,0.85:-53.90211808546633,1080.8547561419787,128,20,3.881408993334766,black,0.85:230.09788191453367,1025.847561419787,368,20,2.1814089933348626,black,0.85:495.0978819145337,1001.8475614197871,368,20,2.1814089933348626,black,0.85:-393.9021180854663,1167.847561419787,368,20,2.1814089933348626,black,0.85:-611.9021180854663,891.8475614197871,368,20,0.6814089933349479,black,0.85:-387.9021180854663,1027.847561419787,164,20,1.447779607694791,black,0.85:-88.90211808546678,806.8475614197871,164,20,1.447779607694791,black,0.85:-331.9021180854668,663.8475614197871,260,20,0.6477796076948366,black,0.85:156.09788191453322,732.8475614197871,260,20,2.7309649148746615,black,0.85:284.0978819145332,705.8475614197871,260,20,1.930964914874707,black,0.85:-38.90211808546678,600.85475614197871,260,20,0.23096491487480367,black,0.85:-131.90211808546678,509.8475614197871,260,20,0.23096491487480367,black,0.85:200.09788191453322,989.8475614197871,134,20,0.6141502220547252,black,0.85:225.09788191453322,880.85475614197871,134,20,0.6141502220547252,black,0.85:106.09788191453322,864.8475614197871,134,20,0.6141502220547252,black,0.85:106.09788191453322,1043.847561419787,29,20,0.6973355292346639,black,0.85:132.09788191453322,965.8475614197871,29,20,0.6973355292346639,black,0.85:73.09788191453322,951.8475614197871,29,20,0.6973355292346639,black,0.85:4.097881914533218,930.85475614197871,29,20,0.6973355292346639,black,0.85:6.097881914533218,862.8475614197871,29,20,0.6973355292346639,black,0.85:23.097881914533218,806.8475614197871,29,20,0.6973355292346639,black,0.85:54.09788191453322,895.8475614197871,29,20,0.6973355292346639,black,0.85:-68.90211808546678,828.8475614197871,29,20,0.6973355292346639,black,0.85:-42.90211808546678,760.85475614197871,29,20,0.6973355292346639,black,0.85:-37.90211808546678,699.8475614197871,29,20,0.6973355292346639,black,0.85"

if not loadCode == None:
    elements = split_string_to_list(loadCode)
    for i in elements:
        scene.append(Rectangle(float(i[0]),float(i[1]),float(i[2]),float(i[3]),float(i[4])*(180/pi),i[5],float(i[6])))

def renderEditor():
    #Define corner polygons for rendering and collision (no recalculation necessary)
    mouse = pygame.mouse.get_pos()
    editPolygon1 = (mouse[0],mouse[1])
    editPolygon2 = (mouse[0] + editWidth * cos(editAngle), mouse[1] - editWidth * sin(editAngle))
    editPolygon3 = (mouse[0] - editHeight * sin(editAngle) + editWidth * cos(editAngle), mouse[1] - editHeight * cos(editAngle) - editWidth * sin(editAngle))
    editPolygon4 = (mouse[0] - editHeight * sin(editAngle), mouse[1] - editHeight * cos(editAngle))

    editPolygon4 = (editPolygon4[0] + 2*(editPolygon1[0] - editPolygon4[0]), editPolygon4[1] + 2*(editPolygon1[1] - editPolygon4[1]))
    editPolygon3 = (editPolygon3[0] + 2*(editPolygon2[0] - editPolygon3[0]), editPolygon3[1] + 2*(editPolygon2[1] - editPolygon3[1]))

    pygame.draw.polygon(screen,"black",[editPolygon1,editPolygon2,editPolygon3,editPolygon4])


def step():
    # COLLISIONS
    collisions = detect_collisions(scene)
    if collisions:
        for i in collisions:
            i[0]

    # UPDATING
    for i in scene:
        i.update()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and editing:
            scene.append(Rectangle(camX - screen.get_width()/2 + pygame.mouse.get_pos()[0],camY + screen.get_height()/2 - pygame.mouse.get_pos()[1],editWidth,editHeight,normalize_angle(-editAngle)*(180/pi),"black",0.8))
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if editing:
                    editing = False
                else:
                    editing = True
            if event.key == pygame.K_g:
                if fly:
                    fly = False
                else:
                    fly = True
            if event.key == pygame.K_r and not isinstance(scene[-1],Ball):
                scene.pop()
            if event.key == pygame.K_TAB:
                code = ""
                for i in scene[1:]:
                    if i == scene[-1]:
                        code += f"{i._x},{i._y},{i._width},{i._height},{i._angle},{i._color},{i._bounciness}"
                    else:
                        code += f"{i._x},{i._y},{i._width},{i._height},{i._angle},{i._color},{i._bounciness}:"
                print("Save code: "+code)
            if event.key == pygame.K_f:
                testBall1._vX = 0
                testBall1._vY = 0
    #LOOP
    for i in range(SUBSTEPS):
        step()
    
    #DRAW
    screen.fill("white")
    for i in scene:
        i.draw()

    # INPUT
    keys = pygame.key.get_pressed()
    if keys[pygame.K_z]:
        for i in scene:
            if isinstance(i,Ball):
                i.exertForce(0,1)
    if keys[pygame.K_s]:
        for i in scene:
            if isinstance(i,Ball):
                i.exertForce(0,-1)
    if keys[pygame.K_q]:
        for i in scene:
            if isinstance(i,Ball):
                i.exertForce(-1,0)
    if keys[pygame.K_d]:
        for i in scene:
            if isinstance(i,Ball):
                i.exertForce(1,0)
    if editing and keys[pygame.K_UP]:
        editHeight -= 3
        if editHeight < 1:
            editHeight = 1
    if editing and keys[pygame.K_DOWN]:
        editHeight += 3
    if editing and keys[pygame.K_LEFT]:
        editWidth -= 3
        if editWidth < 1:
            editWidth = 1
    if editing and keys[pygame.K_RIGHT]:
        editWidth += 3
    if editing and keys[pygame.K_RSHIFT]:
        editAngle += 0.1
    
    camX = testBall1._x
    camY = testBall1._y
    if editing:
        renderEditor()

    screen.blit(update_fps(), (0,0))
    clock.tick(frameRate)
    pygame.display.flip()

pygame.quit()
