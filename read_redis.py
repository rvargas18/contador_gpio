import redis
import cronus.beat as beat
from datetime import datetime as dt


r = redis.Redis('localhost')

frecuencia = 1. / 60.    # en Hz
i = 0
beat.set_rate(frecuencia)
while beat.true():
    print("\nCiclo #{}".format(i))
    now = dt.now()
    print(now)
    for c in range(10):
        count = r.get('in_{}'.format(c))
        _count = int(count) if count else 0
        print('Count {}: {}'.format(c, _count))
    i += 1
    beat.sleep()
