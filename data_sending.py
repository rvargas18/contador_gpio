# -*- coding: utf-8 -*-
import redis
import cronus.beat as beat
from datetime import datetime as dt
from datetime import timezone as tz
import settings as settings


# Funciones generales
def sending(_type, data, now):
    """
    Envia los datos de contadores
    """
    port = 21678
    server = settings.server
    print(f"Enviando a {server} puerto {port}")
    # sock = socket.create_connection((server, port))
    now_utc = now.replace(tzinfo=tz.utc)
    timestamp = int(now_utc.timestamp())
    message = f"{_type} {timestamp} {data}\n"
    # sock.sendall(message)
    # x = sock.recv(port)
    # sock.close()
    return message


# MAIN
print("Iniciando programa...")
print(f"Pines a Enviar: {settings.pines}\n")

# Inicializa redis
r = redis.Redis('localhost', decode_responses=True)

# Ciclo de envío cada 1 minuto
frecuencia = 1. / 60.    # en Hz
i = 0
beat.set_rate(frecuencia)
while beat.true():
    print(f"\nCiclo #{i}")
    now = dt.now().replace(microsecond=0)
    print(now)
    # verifica que el proceso de lectura esté en ejecución
    status = r.get('read_execution')
    devices = settings.devices
    if status == "True":
        for pin in settings.pines:
            # Obtine Datos desde Redis
            _count = r.get(f'counter_{pin}')
            count = int(_count) if _count else 0
            _state = r.get(f'state_{pin}')
            state = int(_state) if _state else 0
            # Formatea los datos
            devid = f"{devices[pin]['devid']}".zfill(4)
            count = f"{int(count)}".zfill(13)
            tpo = "0".zfill(13)
            sd_id = f"{i}".zfill(4)[:4]
            data = f"{devid} {state} {count} {tpo} {sd_id}"
            # Envia datos
            try:
                send = sending('update', data, now)
                print(send)
            except Exception as e:
                print(f"[socket Error]: {e}\nNo se han enviado datos")
    else:
        print("[ERROR]: El script de lectura no esta en ejecucion")
    i += 1
    beat.sleep()
