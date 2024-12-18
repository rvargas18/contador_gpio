import redis
import cronus.beat as beat
from datetime import datetime as dt
from datetime import timezone as tz
import settings as settings
import socket


# Funciones generales
def sending(_type, data, now):
    """
    Envia los datos de estado ON/OFF
    """
    port = 21678
    sock = socket.create_connection(('localhost', port))
    now_utc = now.replace(tzinfo=tz.utc)
    timestamp = now_utc.timestamp()
    message = "{} {} {}\n".format(_type, timestamp, data)
    sock.sendall(message)
    x = sock.recv(port)
    sock.close()
    return x

def zsf_osf(idx, count_t, delta):
    """
    Genera el estado ON/OFF a partir del conteo
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


# Inicializa Datos de las máquinas
r = redis.Redis('localhost')
ini = dt.now()
devices = settings.devices
for dev in devices:
    devices[dev]['date_read'] = ini
    count = r.get('counter_{}'.format(dev))
    devices[dev]['count_t'] = int(count) if count else 0

# Ciclos de Lectura
frecuencia = 1.    # en Hz
i = 0
beat.set_rate(frecuencia)
while beat.true():
    # print("\nCiclo #{}".format(i))
    now = dt.now()
    # verifica que el proceso de lectura esté en ejecución
    status = r.get('read_execution')
    if status == b"True":
        for pin in settings.pines:
            devid = "{}".format(devices[pin]['devid']).zfill(4)
            delta_read = (now - devices[pin]['date_read']).total_seconds() if i != 0 else 1
            count = r.get('counter_{}'.format(pin))
            count_t = int(count) if count else 0
            if count_t < devices[pin]['count_t']:
                devices[pin]['count_t'] = count_t
            # actualiza fecha ultima lectura
            devices[pin]['date_read'] = now
            # obtiene el estado segun nuevo acumulado
            state = zsf_osf(pin, count_t, delta_read)
            # actualiza acumulado
            devices[pin]['count_t'] = count_t
            # revisa si debe enviar nuevo estado
            if state != devices[pin]['state']:
                sd_id = "{}".format(i).zfill(4)[:4]
                data = "{} {} {}".format(devid, state, sd_id)
                print("\tSending stamp")
                print("\t\t{}".format(data))
                # actualiza estado despues de enviar
                devices[pin]['state'] = state
                r.set('state_{}'.format(pin), state)
                # Envia los datos
                # try:
                #     send = sending('stamp', data, now)
                #     print(send)
                #     # actualiza estado despues de enviar
                #     devices[pin]['state'] = state
                #     r.set('state_{}'.format(pin), state)
                # except Exception as e:
                #     print("[socket Error]: {}\nNo se han enviado datos".format(e))
    else:
        print("[ERROR]: El script de lectura no esta en ejecucion")
    i += 1
    beat.sleep()
