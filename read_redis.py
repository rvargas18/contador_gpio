import redis
import cronus.beat as beat
from datetime import datetime as dt
import pines


r = redis.Redis('localhost')
pins = pines.pins
frecuencia = 1. / 60.    # en Hz
i = 0
beat.set_rate(frecuencia)
while beat.true():
    print("\nCiclo #{}".format(i))
    now = dt.now()
    print(now)
    for pin in pins:
        count = r.get('input_{}'.format(pin))
        _count = int(count) if count else 0
        print('Count pin {}: {}'.format(pin, _count))
    i += 1
    beat.sleep()
