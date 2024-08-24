import RPi.GPIO as GPIO
import time
import redis

rd = redis.Redis('localhost')

GPIO.setmode(GPIO.BOARD)
GPIO.setup(3, GPIO.IN)
count = 0
old_data = 0

print("Count: {}".format(count))
for x in range(100):
    input = GPIO.input(3)
    if input != old_data:
        old_data = input
        if input:
            count += 1
            rd.set('{}'.format('in_3'), count)
print("Count: {}".format(count))

