from gpiozero import Button
import pines


counter = 0
def increment_counter():
    global counter
    counter += 1

button = Button(pines.pins[0])

while True:
    button.when_pressed = increment_counter
    button.when_released = print(counter)

