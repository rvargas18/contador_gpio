"""
GPIO PINS

BCM: 2, 3, 4, 17, 27, 22, 5, 6, 13, 19, 26, 14, 15, 18, 23, 24, 25, 12, 16, 20, 21
BOARD: 3, 5, 7, 8, 10, 11, 12, 13, 15, 16, 18, 22, 29, 31, 32, 33, 35, 36, 37, 38, 40
"""

pines = [21, 26]    # BCM

devices = {
    pin : {
        'devid': 1057, 'count_t': 0, 'state': 0, 'date_read': 0, 'zsf': True, 
        'tl_zs': 10, 'time_zs': 0, 'osf': True, 'tl_os': 15, 'time_os': 0, 'aux_on': False
    } for pin in pines
}
