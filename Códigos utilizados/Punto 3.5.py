
import network
import time
import math

# Configuracion de la prueba
SSID_OBJETIVO = "EDIEMYPAULA"
ARCHIVO_CSV = "rssi_distancia5.csv"
NUM_MUESTRAS = 10
ESPERA_S = 1

# Activar la interfaz WiFi en modo estacion
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

def buscar_rssi():
    """Escanea las redes y devuelve el RSSI del celular."""
    try:
        redes = wlan.scan()

        for red in redes:
            ssid = red[0].decode("utf-8", "ignore")
            rssi = red[3]

            if ssid == SSID_OBJETIVO:
                return rssi

    except Exception as error:
        print("Error durante el escaneo:", error)

    return None


def medir_punto(distancia):
    """Realiza diez mediciones y calcula el promedio."""
    muestras = []

    print("\nMidiendo a", distancia, "metros")

    for i in range(NUM_MUESTRAS):
        rssi = buscar_rssi()

        if rssi is not None:
            muestras.append(rssi)
            print("Muestra", i + 1, ":", rssi, "dBm")
        else:
            print("Muestra", i + 1, ": red no detectada")

        time.sleep(ESPERA_S)

    if muestras:
        promedio = sum(muestras) / len(muestras)
        print("Muestras validas:", len(muestras))
        print("RSSI promedio:", round(promedio, 2), "dBm")
    else:
        promedio = None
        print("No se detecto la red en este punto.")

    return muestras, promedio


print("MEDICION RSSI VS DISTANCIA")
print("Red objetivo:", SSID_OBJETIVO)
print("Activa el punto de acceso del celular.")
print("Introduce la distancia en metros.")
print("Escribe 0 para finalizar.")

# Crear archivo y encabezado
with open(ARCHIVO_CSV, "w") as archivo:
    encabezado = "distancia_m"
    for i in range(NUM_MUESTRAS):
        encabezado += ",muestra_" + str(i + 1)
    encabezado += ",muestras_validas,promedio_rssi_dbm\n"
    archivo.write(encabezado)

    while True:
        try:
            distancia = float(input("\nDistancia en metros (0 termina): "))

            if distancia == 0:
                break

            if not math.isfinite(distancia) or distancia < 0:
                print("Introduce una distancia positiva.")
                continue

            muestras, promedio = medir_punto(distancia)

            # Guardar las diez muestras y el promedio
            fila = str(distancia)

            for i in range(NUM_MUESTRAS):
                if i < len(muestras):
                    fila += "," + str(muestras[i])
                else:
                    fila += ","

            fila += "," + str(len(muestras)) + ","

            if promedio is not None:
                fila += str(round(promedio, 2))

            archivo.write(fila + "\n")
            archivo.flush()

            print("Datos guardados en", ARCHIVO_CSV)

        except ValueError:
            print("Entrada invalida. Introduce un numero.")
        except KeyboardInterrupt:
            print("\nMedicion interrumpida.")
            break

print("\nPrueba finalizada.")
print("Archivo generado:", ARCHIVO_CSV)
