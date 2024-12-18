import redis
import cronus.beat as beat
from datetime import datetime as dt
import settings as settings


r = redis.Redis('localhost')

frecuencia = 1. / 60.    # en Hz
i = 0
beat.set_rate(frecuencia)
while beat.true():
    print("\nCiclo #{}".format(i))
    now = dt.now()
    print(now)
    for pin in settings.pines:
        count = r.get('counter_{}'.format(pin))
        _count = int(count) if count else 0
        print('Count pin {}: {}'.format(pin, _count))
    i += 1
    beat.sleep()
