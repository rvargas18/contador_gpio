# -*- coding: utf-8 -*-
import redis
import cronus.beat as beat
from datetime import datetime as dt
from datetime import timezone as tz
import settings as settings
import socket
import threading
import queue

# Cola para el envío de datos
send_queue = queue.Queue()

# Función de envío de datos
def sending(_type, data, now):
    """
    Envia los datos de contadores
    """
    buffer = 1024
    port = 21678
    server = f"{settings.server}"
    print(f"Enviando a {server} puerto {port}")
    sock = socket.create_connection((server, port))
    now_utc = now.replace(tzinfo=tz.utc)
    timestamp = int(now_utc.timestamp())
    message = f"{_type} {timestamp} {data}\n".encode('utf-8')
    sock.sendall(message)
    resp = sock.recv(buffer)
    sock.close()
    return message, resp

# Hilo para procesar la cola de envío
def sending_worker():
    """
    Hilo que procesa los datos de la cola para enviarlos.
    """
    while True:
        try:
            # Obtiene datos de la cola
            _type, data, now = send_queue.get()
            if _type is None:  # Señal para detener el hilo
                break
            # Llama a la función de envío
            msg, resp = sending(_type, data, now)
            print(f"Respuesta: {resp}")
        except Exception as e:
            print(f"[socket Error]: {e}\nNo se han enviado datos")
        finally:
            send_queue.task_done()

# Inicia el hilo de envío
thread = threading.Thread(target=sending_worker, daemon=True)
thread.start()

# MAIN
print("\nIniciando programa...")
print(f"Pines a Enviar: {settings.pines}")

# Inicializa Redis
r = redis.Redis('localhost', decode_responses=True)

# Ciclo de envío cada 1 minuto
frecuencia = 1. / 60.    # en Hz
i = 0
beat.set_rate(frecuencia)
while beat.true():
    print(f"\nCiclo #{i}")
    now = dt.now().replace(microsecond=0)
    print(now)
    # Verifica que el proceso de lectura esté en ejecución
    status = r.get('read_execution')
    devices = settings.devices
    if status == "True":
        for pin in settings.pines:
            # Obtiene Datos desde Redis
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
            # Coloca los datos en la cola
            send_queue.put(('update', data, now))
    else:
        print("[ERROR]: El script de lectura no está en ejecución")
    i += 1
    beat.sleep()

# Finaliza el hilo al terminar el programa
send_queue.put((None, None, None))
thread.join()
