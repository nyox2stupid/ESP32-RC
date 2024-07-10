import pygame
import sys
import time
import serial

def display_text(surface, text, position, color, font_size=16):
    font = pygame.font.SysFont('Arial', font_size)
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, position)

def draw_selection_screen(screen, selected_keys, selecting):
    screen.fill((0, 0, 0))
    display_text(screen, f"Press key for {selecting}", (20, 20), (255, 255, 255), 24)
    y = 60
    for action, key in selected_keys.items():
        display_text(screen, f"{action}: {pygame.key.name(key) if key else 'None'}", (20, y), (255, 255, 255), 24)
        y += 40
    pygame.display.flip()

def initialize_pygame():
    pygame.init()
    return pygame.display.set_mode((400, 300))

def select_keys(screen):
    selected_keys = {'throttle': None, 'steering_left': None, 'steering_right': None}
    selecting = 'throttle'
    while selecting:
        draw_selection_screen(screen, selected_keys, selecting)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                selected_keys[selecting] = event.key
                selecting = {
                    'throttle': 'steering_left',
                    'steering_left': 'steering_right',
                    'steering_right': None
                }[selecting]
    return selected_keys

def initialize_joystick():
    joystick = None
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
    return joystick

def smooth_throttle(throttle, throttle_value):
    if throttle and throttle_value != 1:
        throttle_value += (1 - throttle_value) * 0.1
    else:
        throttle_value -= throttle_value * 0.1
    return throttle_value

def update_screen(screen, joystick, selected_keys, ser):
    steering_value, throttle_value = 0, 0

    if joystick:
        steering_value = joystick.get_axis(0)
        # throttle_value = joystick.get_axis(1)

    keys = pygame.key.get_pressed()
    throttle_value = smooth_throttle(keys[selected_keys['throttle']], throttle_value)
    # if keys[selected_keys['throttle']]:
        # throttle_value = 1
    if keys[selected_keys['steering_left']]:
        steering_value = -1
    if keys[selected_keys['steering_right']]:
        steering_value = 1

    angle = int((steering_value * -1 + 1) * 90)
    ser.write(f"{angle}\n".encode())

    screen.fill((0, 0, 0))

    display_text(screen, f"Steering: {steering_value}", (25, 30), (255, 255, 255))
    display_text(screen, f"Throttle: {throttle_value}", (25, 105), (255, 255, 255))
    pygame.draw.rect(screen, (0, 0, 255), ((25, 125), (throttle_value * 350, 50)))
    pygame.draw.rect(screen, (255, 255, 255), ((25, 125), (350, 50)), 3)

    if steering_value > 0:
        pygame.draw.rect(screen, (0, 255, 0), ((200, 50), (steering_value * 175, 50)))
    elif steering_value < 0:
        pygame.draw.rect(screen, (0, 255, 0), (((steering_value + 1) * 175 + 25, 50), (steering_value * -175, 50)))
    pygame.draw.rect(screen, (255, 255, 255), ((25, 50), (350, 50)), 3)

    pygame.display.flip()

def main():
    screen = initialize_pygame()
    pygame.display.set_caption('Input Selection')

    selected_keys = select_keys(screen)

    joystick = initialize_joystick()
    axnum = joystick.get_numaxes() if joystick else 0
    screen = pygame.display.set_mode((400, 225 * (axnum + 1)))
    pygame.display.set_caption('Steering Wheel Input')
    ser = serial.Serial('/dev/ttyUSB0', 115200)  # Change the port name as needed

    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            update_screen(screen, joystick, selected_keys, ser)
    
    except KeyboardInterrupt:
        pygame.quit()
        ser.close()
        sys.exit()

if __name__ == "__main__":
    main()
