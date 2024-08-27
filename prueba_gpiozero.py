from gpiozero import Button
from signal import pause
import pines

# Inicializa el contador
counter = 0

# Define una función para incrementar el contador
def increment_counter():
    global counter
    counter += 1

# Define una función para imprimir el contador
def print_counter():
    print(f"Contador: {counter}")

# Configura el botón con un tiempo de debounce de 0.2 segundos (ajustable según sea necesario)
button = Button(pines.pins[0], bounce_time=0.2)

# Asigna las funciones a los eventos del botón
button.when_pressed = increment_counter
button.when_released = print_counter

# Mantén el programa en ejecución
pause()
