import RPi.GPIO as GPIO
import redis
import threading


# Start Setup
rd = redis.Redis('localhost')
GPIO.setmode(GPIO.BOARD)
pins = [3, 5, 7, 11, 13, 15, 19, 21, 23, 29]
for pin in pins:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
counters = {
    pin: 0 for pin in pins
}
old_data = {
    pin: 0 for pin in pins
}

# Function to count pulses
def count_pulses(index):
    global old_data
    global counters
    while True:
        input = GPIO.input(index)
        if input != old_data[index]:
            old_data[index] = input
            if input == GPIO.HIGH:
                counters[index] += 1
                rd.set('{}'.format('input_{}'.format(index)), counters[index])

# Start Threads
threads = []
for pin in pins:
    threads.append(threading.Thread(target=count_pulses, args=(pin,)))
    threads[-1].start()


