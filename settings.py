import redis

r = redis.Redis('localhost', decode_responses=True)

"""
Seteo de Datos
"""

"""
Servidor para envio de datos
"""
_server = r.get('server')
# Si no existe la llave 'server' en redis asigna valor por defecto
server = _server if _server else 'localhost'
print(f"servidor: {server}")

"""
Pines GPIO
BCM: 2, 3, 4, 17, 27, 22, 5, 6, 13, 19, 26, 14, 15, 18, 23, 24, 25, 12, 16, 20, 21
BOARD: 3, 5, 7, 8, 10, 11, 12, 13, 15, 16, 18, 22, 29, 31, 32, 33, 35, 36, 37, 38, 40
"""
_r_pines = r.get('pines')
# Si no existe la llave 'pines' en redis asigna valor por defecto, los 8 pines
r_pines = _r_pines if _r_pines else "5, 6, 13, 16, 19, 20, 21, 26"
pines = [int(pin) for pin in r_pines.split(",") if r.get(f'devid_{int(pin)}')]
print(f"pines: {pines}")

"""
Parametros de las Maquinas a utilizar, depende de pines
"""
devices = {
    pin : {
        'devid': int(r.get(f'devid_{pin}')),
        'count_t': 0,
        'state': 0,
        'date_read': 0,
        'zsf': True if r.get(f'zsf_{pin}') == '1' else False, 
        'tl_zs': int(r.get(f'tl_zs_{pin}')) if r.get(f'tl_zs_{pin}') else 10,
        'time_zs': 0,
        'osf': True if r.get(f'osf_{pin}') == '1' else False,
        'tl_os': int(r.get(f'tl_os_{pin}')) if r.get(f'tl_zs_{pin}') else 15,
        'time_os': 0,
        'aux_on': False
    } for pin in pines if r.get(f'devid_{pin}')
}
print("Maquinas")
for dev in devices:
    print("pin:", f"{dev}".zfill(2), devices[dev])