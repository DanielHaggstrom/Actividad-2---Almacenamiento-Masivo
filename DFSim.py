from Master import Master
from Slave import Slave
import time

############################################
#               NO TOCAR                   #
############################################

SLAVE_NUM = 400000  # Numero de nodos esclavos a simular
SLAVE_MEMORY = 64  # Tamanyo maximo de la memoria de cada nodo esclavo
MASTER_MEMBLOCK = 16  # Tamanyo del bloque de memoria de la base de datos, expresado en numero de caracteres

slaveNodes = {"S" + str(k): Slave("S" + str(k), SLAVE_MEMORY) for k in range(0, SLAVE_NUM)}
masterNode = Master(slaveNodes, MASTER_MEMBLOCK)

# Devuelve una secuencia que apaga el simulador
def quit(args):
    print("Apagando el simulador")
    return "quit"


# Comando de lectura de un fichero almacenado en el DFS
def read(*args):
    text = masterNode.read(*args)
    return text


# Comando de escritura de un fichero almacenado al DFS
def write(*args):
    return masterNode.write(*args)


############################################
#       MODIFICAR A PARTIR DE AQUI         #
############################################
# En esta seccion se pueden incluir nuevos comandos como "def write" o similares

def erase(*args):
    return masterNode.erase(*args)

def debug(*args):
    masterNode.debug()
    return ""

def help(*args):
    return "Los comandos son: escribir, leer, borrar, debug, ayuda y salir.\nSalir, debug y ayuda no toman parámetros." \
           "\nLeer y borrar toman un parámetro, el nombre del archivo que se quiere leer o borrar.\nEscribir toma dos," \
           " que son el modo de escritura y el nombre del archivo.\nLos modos de escritura son: hasta_maxima_carga (a)," \
           " secuencial (b), aleatorio (c) y primero_vacio (d).\nSe puede pasar tanto el nombre del modo como su letra" \
           " asociada, para mayor comodidad."

commands = {
    "salir": quit,
    "leer": read,
    "escribir": write,
    "borrar": erase,
    "debug": debug,
    "ayuda": help
}

out = False

# Bucle principal de ejecucion
while not out:
    command = input("[DFSim]>> ")  # Introducir una instruccion
    parsed = [i for i in command.split(" ") if i != '']  # Separar la instruccion
    f = parsed[0]  # Extraer el nombre del comando
    args = tuple([x for i, x in enumerate(parsed) if i != 0])  # Extraer los argumentos introducidos

    if f in commands.keys():
        start = time.time()
        output = commands[f](args)  # Ejecucion de la instruccion
        end = time.time()
    else:
        print("Comando desconocido")
        output = "none"

    if output is "quit":
        out = True  # Salir del programa
    print(output)
    print("Operación ejecutada en " + str(end - start) + " segundos.")