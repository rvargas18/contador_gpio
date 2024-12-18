from gpiozero import Button
import redis
import settings
import time

# Inicializa los contadores globales y en Base de Datos Redis
counters = {
    pin: 0 for pin in settings.pines
}
r = redis.Redis('localhost')
for pin in settings.pines:
    r.set('counter_{}'.format(pin), 0)

# Configura el botón con un tiempo de debounce de 0.1 segundos
buttons = {
    pin: Button(pin, bounce_time=0.1) for pin in settings.pines
}

# Función para contar los pulsos
def count_pulses(pin):
    def increment_counter():
        counters[pin] += 1
        r.set('counter_{}'.format(pin), counters[pin])

    # Asignar la función al evento when_pressed
    buttons[pin].when_pressed = increment_counter

# Función para limpiar recursos
def close_all():
    for pin in buttons:
        buttons[pin].close()

# Main
print("Iniciando programa...")
print("Pines: {}".format(settings.pines))

# Configurar eventos para todos los pines
for pin in settings.pines:
    count_pulses(pin)

# Mantener el programa corriendo
try:
    r.set('read_execution', 'True')
    while True:
        time.sleep(1)  # Reducir el uso de CPU
except KeyboardInterrupt:
    print("Programa interrumpido por el usuario.")
finally:
    r.set('read_execution', 'False')
    close_all()
    print("GPIO limpiado y programa terminado.")
