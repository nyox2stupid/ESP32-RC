import pygame
import sys
import serial
import time

def select_joystick():
    pygame.init()
    pygame.joystick.init()
    
    joystick_count = pygame.joystick.get_count()
    if joystick_count == 0:
        print("No joystick devices found.")
        sys.exit(1)

    print("Available joystick devices:")
    for i in range(joystick_count):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
        print(f"{i}: {joystick.get_name()}")

    # Select joystick device
    device_idx = int(input("Enter the index of the joystick device you want to use: "))
    if device_idx < 0 or device_idx >= joystick_count:
        print("Invalid index.")
        sys.exit(1)

    joystick = pygame.joystick.Joystick(device_idx)
    joystick.init()
    
    # Print available axes and their current values
    print("Available axes and current values:")
    num_axes = joystick.get_numaxes()
    for i in range(num_axes):
        print(f"Axis {i}: {joystick.get_axis(i)}")

    # Select axis for steering
    axis_idx = int(input("Enter the index of the axis you want to use for steering: "))
    if axis_idx < 0 or axis_idx >= num_axes:
        print("Invalid axis index.")
        sys.exit(1)

    return joystick, axis_idx

def display_text(surface, text, position, color, font_size=16):
    font = pygame.font.SysFont('Arial', font_size)
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, position)

def main():
    joystick, axis_idx = select_joystick()

    # Initialize serial communication
    try:
        ser = serial.Serial('COM5', 115200, timeout=1)  # Change the port name as needed
        time.sleep(2)  # Wait for the serial connection to initialize
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        sys.exit(1)

    pygame.init()
    axnum = joystick.get_numaxes()
    screen = pygame.display.set_mode((400, 100 * axnum))
    pygame.display.set_caption('Steering Wheel Input')
    
    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    ser.close()
                    sys.exit()

            # Get current value of the selected axis
            steering_value = joystick.get_axis(axis_idx)

            # Convert steering value to servo angle (0 to 180)
            angle = int((steering_value * -1 + 1) * 90)
            
            # Send the angle to the ESP32
            try:
                ser.write(f"{angle}\n".encode())
            except serial.SerialException as e:
                print(f"Error writing to serial port: {e}")

            screen.fill((0, 0, 0))  # Clear screen

            display_text(screen, str(steering_value), (25, 5), (255, 255, 255))

            if steering_value > 0:
                pygame.draw.rect(screen, (0, 255, 0), ((200, 25), (steering_value * 175, 50)))
            elif steering_value < 0:
                pygame.draw.rect(screen, (0, 255, 0), (((steering_value + 1) * 175 + 25, 25), (steering_value * -175, 50)))

            pygame.draw.rect(screen, (255, 255, 255), ((25, 25), (350, 50)), 3)

            pygame.display.flip()
    
    except KeyboardInterrupt:
        pygame.quit()
        ser.close()
        sys.exit()

if __name__ == "__main__":
    main()
