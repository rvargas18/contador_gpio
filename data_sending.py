# -*- coding: utf-8 -*-
import redis
from datetime import datetime as dt
from datetime import timezone as tz
import settings as settings
import socket
import time


# Configura Redis
r = redis.Redis('localhost', decode_responses=True)

# Función de envío de datos
def sending(_type, data, now):
    """
    Envia los mesajes al servidor
    """
    buffer = 1024
    port = 21678
    server = f"{settings.server}"
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
    Procesa los datos desde Redis (cola persistente).
    """
    retries = 1
    while True:
        try:
            # Extrae los mensajes desde el más antiguo al más nuevo
            queued_message = r.lpop('messages')
            if queued_message:
                _type, data, timestamp = queued_message.split('|')
                now = dt.fromtimestamp(int(timestamp), tz=tz.utc)
                # Intenta enviar el mensaje
                msg, resp = sending(_type, data, now)
                print(f"Mensaje: {msg} -> Respuesta: {resp}")
                if b'UPDATED' not in resp and b'STAMPED' not in resp:
                    print("Respuesta no Valida. Reinsertando el mensaje en la cola...")
                    # Reinsertar el mensaje al inicio de la cola
                    r.lpush('messages', queued_message)
                    retry_delay = min(2 * retries, 60)
                    retries += 1
                    time.sleep(retry_delay)  # Espera antes de reintentar
                else:
                    retries = 1
            else:
                # Si no hay mensajes, espera un momento antes de reintentar
                time.sleep(1)
        except Exception as e:
            print(f"[Error general]: {e}")
            print("Reinsertando el mensaje en la cola...")
            # Reinsertar el mensaje al inicio de la cola
            r.lpush('messages', queued_message)
            # Espera antes de reintentar
            retry_delay = min(2 * retries, 60)
            retries += 1
            time.sleep(retry_delay)

# MAIN
print("\nIniciando programa...")
sending_worker()