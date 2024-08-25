import redis
import cronus.beat as beat
from datetime import datetime as dt


r = redis.Redis('localhost')
pins = [3, 5, 7, 11, 13, 15, 19, 21, 23, 29]
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
        print('Count {}: {}'.format(pin, _count))
    i += 1
    beat.sleep()
