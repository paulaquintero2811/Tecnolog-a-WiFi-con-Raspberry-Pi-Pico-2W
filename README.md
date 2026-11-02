# Tecnología WiFi con Raspberry Pi Pico 2W

## Descripción
En este laboratorio se implementaron y analizaron diferentes funcionalidades de comunicación inalámbrica utilizando tarjetas Raspberry Pi Pico 2W y módulos NRF24L01.

La práctica se dividió en dos partes. En la primera se exploraron las capacidades WiFi de la Raspberry Pi Pico 2W, realizando identificación de dirección MAC, escaneo de redes, implementación de puntos de acceso y servidores web, control de un LED, lectura del ADC, medición de intensidad de señal RSSI y observación de señales WiFi mediante un analizador de espectro.

En la segunda parte se implementó un sistema de comunicación inalámbrica entre dos Raspberry Pi mediante módulos NRF24L01, integrando una interfaz web para configurar los parámetros de transmisión y recepción.

## Objetivos
- Explorar las funciones de conectividad WiFi de la Raspberry Pi Pico 2W.
- Identificar redes inalámbricas disponibles y consultar sus parámetros.
- Medir la intensidad de señal RSSI a diferentes distancias.
- Observar señales WiFi mediante un analizador de espectro.
- Implementar servidores web para controlar y visualizar información desde un navegador.
- Configurar la comunicación entre dos módulos NRF24L01.
- Comprobar la transmisión y recepción de mensajes mediante radiofrecuencia.

## Materiales y herramientas
- 2 tarjetas Raspberry Pi Pico 2W.
- 2 módulos NRF24L01.
- 2 pantallas OLED SSD1306.
- Botones físicos.
- LED externo y resistencia.
- Computador.
- Entorno de programación Thonny.
- MicroPython.
- Analizador de espectro Anritsu.
- Redes WiFi y dispositivos para realizar las pruebas.

## Desarrollo del laboratorio

### 1. Implementación y pruebas de conectividad WiFi

Se realizaron diferentes pruebas para explorar las funciones inalámbricas de la Raspberry Pi Pico 2W:

- Identificación de la dirección MAC de la tarjeta.
- Escaneo de redes WiFi disponibles, obteniendo información como SSID, BSSID, canal y RSSI.
- Configuración de un punto de acceso WiFi.
- Implementación de un servidor web para controlar el LED integrado desde una página HTML.
- Generación de tráfico WiFi intermitente y sostenido para observar la señal mediante un analizador de espectro.
- Lectura del convertidor analógico-digital ADC0 (GP26) y visualización de los valores desde una página web.
- Medición del RSSI a diferentes distancias para analizar el comportamiento de la señal inalámbrica.

### 2. Comunicación inalámbrica con NRF24L01

Se conectaron dos módulos NRF24L01 a sus respectivas Raspberry Pi Pico 2W mediante el protocolo SPI.

**Conexiones SPI del NRF24L01:**

| Pin NRF24L01 | Pin Raspberry Pi |
|---|---|
| CE | GP17 |
| CSN | GP20 |
| SCK | GP18 |
| MOSI | GP19 |
| MISO | GP16 |
| VCC | 3.3 V |
| GND | GND |

**Conexiones de la pantalla OLED:**

| Pin OLED | Pin Raspberry Pi |
|---|---|
| SDA | GP4 |
| SCL | GP5 |
| VCC | 3.3 V |
| GND | GND |

También se utilizaron botones en los pines GP10 y GP11, y un LED externo conectado al GP12.

Se desarrolló un programa en MicroPython para configurar los módulos y permitir la transmisión y recepción de mensajes. Posteriormente, se integró una interfaz web que permitió modificar los parámetros de comunicación desde un navegador.

### 3. Parámetros de configuración del NRF24L01

- Canal de operación: entre 70 y 80.
- Velocidades de transmisión: 250 kbps, 1 Mbps y 2 Mbps.
- Potencias de transmisión: -18 dBm, -12 dBm, -6 dBm y 0 dBm.
- Modos de operación: transmisión (TX) y recepción (RX).
- Tipos de envío: único (UNICO) y continuo (LOOP).
- Tamaño de carga útil: 32 bytes.

## Resultados principales

- Se identificaron redes WiFi cercanas mediante cinco barridos consecutivos.
- Se implementó un punto de acceso WiFi y se controló el LED de la tarjeta desde una página web.
- Se observó actividad de transmisión WiFi mediante el analizador de espectro, registrando un nivel de -64,78 dBm a 2432,8 MHz.
- Se realizó una lectura del ADC0 con un valor digital de 12563, equivalente a una tensión estimada de 0,633 V.
- En las mediciones de RSSI se observó una tendencia general de disminución de la intensidad de señal al aumentar la distancia.
- Se alcanzó una distancia máxima experimental de 66 metros, con un RSSI promedio de -87 dBm.
- Se comprobó la comunicación entre los dos módulos NRF24L01 utilizando el canal 71 (2471 MHz), una velocidad de 1 Mbps y una potencia de 0 dBm.
- Se verificó la recepción del mensaje **PAULA QUINTERO**, incluso cuando las dos Raspberry Pi estaban conectadas a redes WiFi diferentes.


## Conclusiones

El laboratorio permitió explorar las capacidades de comunicación WiFi de la Raspberry Pi Pico 2W y comprobar su utilidad para desarrollar aplicaciones de control y adquisición de datos mediante servidores web.

También se analizó el comportamiento de la intensidad de señal RSSI con respecto a la distancia y se observó la actividad inalámbrica mediante un analizador de espectro.

Finalmente, se comprobó que los módulos NRF24L01 permiten establecer una comunicación independiente de la conexión WiFi, logrando transmitir y recibir mensajes entre dos Raspberry Pi conectadas a redes diferentes.

## Autores

**Paula Quintero y Ediem Valero**

Universidad Militar Nueva Granada  
Ingeniería de Telecomunicaciones  
Asignatura: Comunicación Digital  
Bogotá, Colombia  
Noviembre de 2026
