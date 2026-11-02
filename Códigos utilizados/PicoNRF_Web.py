# Comunicaciones Digitales - UMNG
# Pico W / Pico 2 W + NRF24L01 + OLED SSD1306 + servidor web
# Copiar este archivo como main.py y index.html a AMBAS Raspberry Pi.
# IMPORTANTE: editar SSID y PASSWORD de cada Raspberry para que sean distintos.

import network
import socket
import time
import gc
import json
from machine import Pin, SPI, I2C
import ssd1306

# ==================== WIFI: EDITAR EN CADA PICO ====================
SSID = 'CAMBIAR_WIFI_PICO_1'
PASSWORD = 'CAMBIAR_CLAVE_PICO_1'

# ==================== NRF24L01 / OLED ====================
HTML_FILE = 'index.html'
PORT = 80

# Pines NRF24L01
CE = Pin(17, Pin.OUT)
CSN = Pin(20, Pin.OUT)
spi = SPI(0, baudrate=1000000, polarity=0, phase=0,
          sck=Pin(18), mosi=Pin(19), miso=Pin(16))
CE.value(0)
CSN.value(1)

# OLED SSD1306: SCL GP5, SDA GP4, direccion 0x3C
i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)
led = Pin(12, Pin.OUT)
led.value(0)

# Registros NRF24L01
CONFIG = 0x00
EN_AA = 0x01
EN_RXADDR = 0x02
SETUP_AW = 0x03
SETUP_RETR = 0x04
RF_CH = 0x05
RF_SETUP = 0x06
STATUS = 0x07
RX_ADDR_P0 = 0x0A
TX_ADDR = 0x10
RX_PW_P0 = 0x11
FIFO_STATUS = 0x17

# Comandos NRF24L01
R_REGISTER = 0x00
W_REGISTER = 0x20
R_RX_PAYLOAD = 0x61
W_TX_PAYLOAD = 0xA0
FLUSH_TX = 0xE1
FLUSH_RX = 0xE2

# Opciones configurables desde la pagina
config = {
    'channel': 76,
    'rate': '1 Mbps',
    'power': '0 dBm',
    'message': 'EDIEM VALERO',
    'mode': 'TX',
    'sending': 'LOOP'
}
MESSAGES = ['EDIEM VALERO', 'PAULA QUINTERO', 'ALFABETO', 'ALFABETO NUMERICO']
RATES = ['250K', '1 Mbps', '2 Mbps']
POWERS = ['-18 dBm', '-12 dBm', '-6 dBm', '0 dBm']
MODES = ['TX', 'RX']
SENDING = ['UNICO', 'LOOP']
last_message = 'Sin mensajes recibidos'
last_event = 'Listo'
last_tx_ms = time.ticks_ms()
last_single_key = None


def write_reg(reg, value):
    CSN.value(0)
    spi.write(bytes([W_REGISTER | reg, value & 0xFF]))
    CSN.value(1)


def read_reg(reg):
    CSN.value(0)
    spi.write(bytes([R_REGISTER | reg]))
    value = spi.read(1, 0xFF)[0]
    CSN.value(1)
    return value


def write_reg_bytes(reg, data):
    CSN.value(0)
    spi.write(bytes([W_REGISTER | reg]))
    spi.write(data)
    CSN.value(1)


def command(cmd):
    CSN.value(0)
    spi.write(bytes([cmd]))
    CSN.value(1)


def rf_setup_value():
    rate_bits = {'250K': 0x20, '1 Mbps': 0x00, '2 Mbps': 0x08}[config['rate']]
    power_bits = {'-18 dBm': 0x00, '-12 dBm': 0x02,
                  '-6 dBm': 0x04, '0 dBm': 0x06}[config['power']]
    return rate_bits | power_bits


def configure_radio():
    CE.value(0)
    write_reg(CONFIG, 0x00)
    time.sleep_ms(3)
    write_reg(EN_AA, 0x00)       # Auto-ACK desactivado
    write_reg(EN_RXADDR, 0x01)   # Pipe 0
    write_reg(SETUP_AW, 0x03)    # Direcciones de 5 bytes
    write_reg(SETUP_RETR, 0x00)
    write_reg(RF_CH, int(config['channel']))
    write_reg(RF_SETUP, rf_setup_value())
    write_reg(RX_PW_P0, 32)      # Payload fijo de 32 bytes
    address = b'RADIO'
    write_reg_bytes(TX_ADDR, address)
    write_reg_bytes(RX_ADDR_P0, address)
    command(FLUSH_TX)
    command(FLUSH_RX)
    write_reg(STATUS, 0x70)      # Limpiar banderas
    if config['mode'] == 'TX':
        write_reg(CONFIG, 0x02)  # Encendido, transmisor
        CE.value(0)
    else:
        write_reg(CONFIG, 0x03)  # Encendido, receptor
        time.sleep_ms(2)
        CE.value(1)
    time.sleep_ms(5)
    update_oled()


def update_oled():
    oled.fill(0)
    oled.text('NRF24L01 / WEB', 0, 0)
    oled.text('Modo: ' + config['mode'], 0, 12)
    oled.text('Canal: ' + str(config['channel']), 0, 22)
    oled.text('Vel: ' + config['rate'], 0, 32)
    oled.text('Pot: ' + config['power'], 0, 42)
    oled.text(config['sending'], 0, 52)
    oled.show()


def transmit(message):
    global last_event
    if config['mode'] != 'TX':
        return False
    data = str(message).encode('utf-8')[:32]
    data = data + bytes(32 - len(data))
    CE.value(0)
    command(FLUSH_TX)
    CSN.value(0)
    spi.write(bytes([W_TX_PAYLOAD]))
    spi.write(data)
    CSN.value(1)
    CE.value(1)
    time.sleep_us(15)
    CE.value(0)
    # Auto-ACK esta desactivado: esto no confirma que el otro Pico lo recibio.
    last_event = 'Trama TX enviada (sin ACK)'
    return True


def receive():
    global last_message, last_event
    if config['mode'] != 'RX':
        return None
    status = read_reg(STATUS)
    if not (status & 0x40):
        return None
    CSN.value(0)
    spi.write(bytes([R_RX_PAYLOAD]))
    data = spi.read(32, 0xFF)
    CSN.value(1)
    write_reg(STATUS, 0x40)
    try:
        message = data.decode('utf-8').replace('\x00', '').strip()
    except Exception:
        message = repr(data)
    if message:
        last_message = message
        last_event = 'Paquete recibido'
        print('Mensaje recibido:', message)
        led.value(1)
        time.sleep_ms(30)
        led.value(0)
        return message
    return None


def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Conectando a WiFi:', SSID)
        wlan.connect(SSID, PASSWORD)
        start = time.ticks_ms()
        while not wlan.isconnected():
            if time.ticks_diff(time.ticks_ms(), start) > 20000:
                raise RuntimeError('No se pudo conectar a WiFi. Revise SSID y PASSWORD.')
            time.sleep_ms(250)
    ip = wlan.ifconfig()[0]
    print('WiFi conectado:', SSID, '| IP:', ip)
    print('Abrir en un dispositivo conectado a esta misma red: http://{}/'.format(ip))
    return wlan, ip


def response(conn, status, body, content_type='application/json; charset=utf-8'):
    if isinstance(body, str):
        body = body.encode('utf-8')
    header = ('HTTP/1.1 {}\r\nContent-Type: {}\r\nContent-Length: {}\r\n'
              'Connection: close\r\nCache-Control: no-store\r\nAccess-Control-Allow-Origin: *\r\n\r\n').format(
                  status, content_type, len(body)).encode()
    conn.send(header)
    if body:
        conn.send(body)


def read_http_request(conn):
    conn.settimeout(1)
    data = b''
    while b'\r\n\r\n' not in data and len(data) < 4096:
        chunk = conn.recv(512)
        if not chunk:
            break
        data += chunk
    if b'\r\n\r\n' not in data:
        raise ValueError('Cabeceras HTTP incompletas')
    head, body = data.split(b'\r\n\r\n', 1)
    lines = head.decode().split('\r\n')
    parts = lines[0].split()
    if len(parts) < 2:
        raise ValueError('Peticion HTTP invalida')
    method, path = parts[0], parts[1].split('?', 1)[0]
    content_length = 0
    for line in lines[1:]:
        if ':' in line:
            key, value = line.split(':', 1)
            if key.strip().lower() == 'content-length':
                content_length = int(value.strip())
    while len(body) < content_length:
        chunk = conn.recv(min(512, content_length - len(body)))
        if not chunk:
            break
        body += chunk
    return method, path, body[:content_length]


def state_json(ip):
    return json.dumps({
        'ok': True, 'ip': ip, 'config': config, 'last_message': last_message,
        'last_event': last_event, 'led': bool(led.value())
    })


def apply_config(new_config):
    global last_event, last_single_key
    channel = int(new_config.get('channel', config['channel']))
    rate = new_config.get('rate', config['rate'])
    power = new_config.get('power', config['power'])
    message = new_config.get('message', config['message'])
    mode = new_config.get('mode', config['mode'])
    sending = new_config.get('sending', config['sending'])
    if channel < 0 or channel > 125:
        raise ValueError('El canal debe estar entre 0 y 125')
    if rate not in RATES or power not in POWERS or mode not in MODES or sending not in SENDING:
        raise ValueError('Opcion de configuracion no valida')
    if message not in MESSAGES:
        raise ValueError('Mensaje no valido')
    changed_radio = (channel != config['channel'] or rate != config['rate'] or
                     power != config['power'] or mode != config['mode'])
    config.update({'channel': channel, 'rate': rate, 'power': power,
                   'message': message, 'mode': mode, 'sending': sending})
    if changed_radio:
        configure_radio()
    else:
        update_oled()
    last_single_key = None
    last_event = 'Configuracion aplicada en este Pico'
    print('Configuracion aplicada:', config)


def handle_client(conn, ip):
    global last_event, last_single_key
    try:
        method, path, body = read_http_request(conn)
        if method == 'OPTIONS':
            response(conn, '204 No Content', b'')
        elif method == 'GET' and path in ('/', '/index.html'):
            try:
                with open(HTML_FILE, 'rb') as f:
                    page = f.read()
                response(conn, '200 OK', page, 'text/html; charset=utf-8')
            except OSError:
                response(conn, '500 Internal Server Error', json.dumps({'ok': False, 'error': 'Falta index.html'}))
        elif method == 'GET' and path == '/api/state':
            response(conn, '200 OK', state_json(ip))
        elif method == 'POST' and path == '/api/config':
            try:
                data = json.loads(body.decode('utf-8'))
                apply_config(data)
                response(conn, '200 OK', state_json(ip))
            except Exception as exc:
                response(conn, '400 Bad Request', json.dumps({'ok': False, 'error': str(exc)}))
        elif method == 'POST' and path == '/api/send':
            if config['mode'] != 'TX':
                response(conn, '409 Conflict', json.dumps({'ok': False, 'error': 'Cambie el modo a TX para transmitir'}))
            else:
                transmit(config['message'])
                response(conn, '200 OK', state_json(ip))
        elif method == 'GET' and path == '/favicon.ico':
            response(conn, '204 No Content', b'')
        else:
            response(conn, '404 Not Found', json.dumps({'ok': False, 'error': 'Ruta no encontrada'}))
    except Exception as exc:
        print('Error HTTP:', exc)
        try:
            response(conn, '400 Bad Request', json.dumps({'ok': False, 'error': str(exc)}))
        except Exception:
            pass
    finally:
        conn.close()
        gc.collect()


def main():
    global last_tx_ms, last_single_key
    update_oled()
    configure_radio()
    wlan, ip = wifi_connect()
    try:
        with open(HTML_FILE, 'rb') as f:
            pass
    except OSError:
        print('ADVERTENCIA: no se encuentra index.html en la raiz del dispositivo')
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', PORT))
    server.listen(2)
    server.settimeout(0.05)
    print('Servidor web listo. NRF24L01 en modo', config['mode'])
    while True:
        try:
            conn, addr = server.accept()
            handle_client(conn, ip)
        except OSError:
            pass  # No habia una solicitud web pendiente.
        receive()
        if config['mode'] == 'TX' and config['sending'] == 'LOOP':
            now = time.ticks_ms()
            if time.ticks_diff(now, last_tx_ms) >= 250:
                transmit(config['message'])
                last_tx_ms = now
                led.value(not led.value())
        elif config['mode'] == 'TX' and config['sending'] == 'UNICO':
            key = (config['message'], config['channel'], config['rate'], config['power'])
            if key != last_single_key:
                # En UNICO se envia una vez tras aplicar una configuracion nueva.
                transmit(config['message'])
                last_single_key = key
        time.sleep_ms(2)


main()
