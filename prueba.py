from gpiozero import Button
import pines

counter = 0
button = Button(pines.pins[0])
button.when_pressed = lambda: counter += 1
button.when_released = lambda: print(counter)

pause()