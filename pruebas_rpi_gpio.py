import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
BUTTON_PIN = 18  # Ajusta este número al pin que estés utilizando
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, bouncetime=200)
    print("Detección de eventos añadida correctamente.")

    while True:
        if GPIO.event_detected(BUTTON_PIN):
            print("Pulsación detectada")
        time.sleep(0.1)
except RuntimeError as e:
    print(f"Error al añadir la detección de eventos: {e}")
finally:
    GPIO.cleanup()
