import pygame

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Circle properties
circle_x = 400
circle_y = 300
radius = 30
speed = 5

running = True
while running:
    # 1. Handle Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 2. Update Position (Move the circle right)
    circle_x += speed
    #circle_y -= speed
    if circle_x > 800 + radius:  # Reset if it goes off screen
        circle_x = -radius

    # 3. Clear Screen (prevents the circle from leaving a "trail")
    screen.fill((255, 255, 255))  # Fills screen with black

    # 4. Draw the Circle inside the loop
    # Syntax: (surface, color_rgb, (x, y), radius)
    pygame.draw.circle(screen, (255, 0, 255), (circle_x, circle_y), radius)

    # 5. Flip/Update the display
    pygame.display.flip()
    clock.tick(60)  # Limits game to 60 FPS

pygame.quit()