from gpiozero import Button
from signal import pause
import threading
import cronus.beat as beat
from datetime import datetime as dt
import redis

# DB redis
r = redis.Redis('localhost')

# Inicializa el contador
pin = 17
counter = 0
counter_2 = 0
# Define una función para incrementar el contador
def increment_counter():
    global counter
    counter += 1
    r.set('counter_17', counter)

# Define una función para imprimir el contador
# frecuencia = 1. / 60.    # en Hz
# beat.set_rate(frecuencia)

def print_counter():
    global counter_2
    while beat.true():
        count_d = counter - counter_2
        print(f"{dt.now()} | Contador: {counter} - {count_d}")
        counter_2 = counter
        beat.sleep()  # Espera 60 segundos antes de imprimir de nuevo

# Configura el botón con un tiempo de debounce de 0.2 segundos (ajustable según sea necesario)
button = Button(pin, bounce_time=0)

# Asigna las funciones a los eventos del botón
button.when_pressed = increment_counter
#button.when_released = increment_counter

# Inicia el hilo para imprimir el contador
# threading.Thread(target=print_counter, daemon=True).start()

# Mantén el programa en ejecución
pause()
