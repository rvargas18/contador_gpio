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


# Funciones generales
def sending(_type, data, now):
    """
    Envia los datos de estado ON/OFF
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

def zsf_osf(idx, count_t, delta):
    """
    Genera el estado ON/OFF a partir del conteo
    y los tiempos ZSF y OSF
    """
    state = devices[idx]['state']
    if devices[idx]['zsf']:
        devices[idx]['time_zs'] += delta
        if count_t - devices[idx]['count_t'] > 0:
            devices[idx]['time_zs'] = 0
            if devices[idx]['osf']:
                devices[idx]['aux_on'] = True
                if devices[idx]['time_os'] > devices[idx]['tl_os']:
                    devices[idx]['time_os'] = devices[idx]['tl_os'] + 1
                    state = 1
            else:
                state = 1
        if devices[idx]['osf'] and devices[idx]['aux_on']:
            devices[idx]['time_os'] += delta
        if devices[idx]['time_zs'] > devices[idx]['tl_zs']:
            devices[idx]['time_zs'] = devices[idx]['tl_zs'] + 1
            state = 0
            devices[idx]['aux_on'] = False
            devices[idx]['time_os'] = 0
    return state

def init_data():
    ini = dt.now()
    devices = settings.devices
    for dev in devices:
        devices[dev]['date_read'] = ini
        count = r.get(f'counter_{dev}')
        devices[dev]['count_t'] = int(count) if count else 0
        devices[dev]['state'] = 0
        r.set(f'state_{dev}', 0)
    return devices

# Inicia el hilo de envío
thread = threading.Thread(target=sending_worker, daemon=True)
thread.start()


# MAIN
print("\nIniciando programa...")
print(f"Pines Procesados: {settings.pines}\n")

# Inicializa Datos de las máquinas
r = redis.Redis('localhost', decode_responses=True)
devices = init_data()

# Ciclos de Lectura cada 1 segundo
frecuencia = 1.    # en Hz
i = 0
beat.set_rate(frecuencia)
while beat.true():
    now = dt.now().replace(microsecond=0)
    # verifica que el proceso de lectura esté en ejecución
    status = r.get('read_execution')
    if status == "True":
        for pin in devices:
            # Obtiene datos de tiempo y contadores
            delta_read = (now - devices[pin]['date_read']).total_seconds() if i != 0 else 1
            count = r.get(f'counter_{pin}')
            count_t = int(count) if count else 0
            if count_t < devices[pin]['count_t']:
                devices[pin]['count_t'] = count_t
            # actualiza fecha ultima lectura
            devices[pin]['date_read'] = now
            # obtiene el estado segun nuevo acumulado
            state = zsf_osf(pin, count_t, delta_read)
            # actualiza acumulado
            devices[pin]['count_t'] = count_t
            # si estado es distinto al anterior envía
            if state != devices[pin]['state']:
                # formatea datos
                devid = f"{devices[pin]['devid']}".zfill(4)
                sd_id = f"{i}".zfill(4)[:4]
                data = f"{devid} {state} {sd_id}"
                # Coloca los datos en la cola de envío
                send_queue.put(('stamp', data, now))
                # actualiza estado despues de enviar
                devices[pin]['state'] = state
                r.set(f'state_{pin}', state)
    else:
        print("[ERROR]: El script de lectura no esta en ejecucion")
        devices = init_data()
    i += 1
    beat.sleep()

# Finaliza el hilo al terminar el programa
send_queue.put((None, None, None))
thread.join()