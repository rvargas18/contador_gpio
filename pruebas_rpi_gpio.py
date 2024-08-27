import RPi.GPIO as GPIO
import time
import pines

# Configura el modo de numeración de pines
GPIO.setmode(GPIO.BCM)

# Define el pin del botón
BUTTON_PIN = pines.pins[0]

# Configura el pin del botón como entrada con resistor pull-up interno
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Inicializa el contador
counter = 0

# Define una función de callback para detectar pulsos
def button_callback(channel):
    global counter
    counter += 1
    print(f"Contador: {counter}")

# Configura el evento de interrupción en flanco de bajada con debounce de 200ms
GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=button_callback, bouncetime=200)

try:
    while True:
        # Mantén el programa en ejecución
        time.sleep(1)
except KeyboardInterrupt:
    print("Programa terminado por el usuario")
finally:
    GPIO.cleanup()
