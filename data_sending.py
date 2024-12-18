# -*- coding: utf-8 -*-
import redis
import cronus.beat as beat
from datetime import datetime as dt
from datetime import timezone as tz
import settings as settings


# Funciones generales
def sending(_type, data, now):
    """
    Envia los datos de estado ON/OFF
    """
    port = 21678
    server = settings.server
    # sock = socket.create_connection((server, port))
    now_utc = now.replace(tzinfo=tz.utc)
    timestamp = int(now_utc.timestamp())
    message = "{} {} {}\n".format(_type, timestamp, data)
    # sock.sendall(message)
    # x = sock.recv(port)
    # sock.close()
    return message

r = redis.Redis('localhost')

frecuencia = 1. / 60.    # en Hz
i = 0
beat.set_rate(frecuencia)
while beat.true():
    print("\nCiclo #{}".format(i))
    now = dt.now()
    print(now)
    # verifica que el proceso de lectura esté en ejecución
    status = r.get('read_execution')
    devices = settings.devices
    if status == b"True":
        for pin in settings.pines:
            # Obtine Datos desde Redis
            _count = r.get('counter_{}'.format(pin))
            count = int(_count) if _count else 0
            _state = r.get('state_{}'.format(pin))
            state = int(_state) if _state else 0
            # Formatea data del mensaje
            devid = "{}".format(devices[pin]['devid']).zfill(4)
            count = "{}".format(int(count)).zfill(13)
            tpo = "0".zfill(13)
            sd_id = "{}".format(i).zfill(4)[:4]
            data = "{} {} {} {} {}".format(devid, state, count, tpo, sd_id)
            # Envia datos
            try:
                send = sending('update', data, now)
                print(send)
            except Exception as e:
                print("[socket Error]: {}\nNo se han enviado datos".format(e))
    else:
        print("[ERROR]: El script de lectura no esta en ejecucion")
    i += 1
    beat.sleep()
