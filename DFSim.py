from Master import Master
from Slave import Slave

############################################
#               NO TOCAR                   #
############################################

SLAVE_NUM = 100  # Numero de nodos esclavos a simular
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
    return masterNode.read(*args)


# Comando de escritura de un fichero almacenado al DFS
def write(*args):
    texto = ""
    for item in list(*args):
        texto = texto + " " + item
    texto = texto[1:]
    aux = True
<<<<<<< HEAD
    answer = 0
    while len(texto) > 0 and aux:
        if not masterNode.isFull():
            answer = answer + masterNode.write(texto[0:MASTER_MEMBLOCK])
            texto = texto[MASTER_MEMBLOCK:]
        else:
            aux = False
    if answer == 0:
        # todo
        return "ok"  # hay que hacer algo para evitar que la frase escrita 'ok' se confunda
    else:
        return "Fallo de escritura"
=======
    while len(texto) > 0 and aux:
        if not masterNode.isFull():
            masterNode.write(texto[0:MASTER_MEMBLOCK])
            texto = texto[MASTER_MEMBLOCK:]
        else:
            aux = False
>>>>>>> master


############################################
#       MODIFICAR A PARTIR DE AQUI         #
############################################
# En esta seccion se pueden incluir nuevos comandos como "def write" o similares

def erase(*args):
    return masterNode.erase()

commands = {
    "salir": quit,
    "leer": read,
    "escribir": write,
    "borrar": erase
}

out = False

# Bucle principal de ejecucion
while not out:
    command = input("[DFSim]>> ")  # Introducir una instruccion
    parsed = [i for i in command.split(" ") if i != '']  # Separar la instruccion
    f = parsed[0]  # Extraer el nombre del comando
    args = tuple([x for i, x in enumerate(parsed) if i != 0])  # Extraer los argumentos introducidos

    if f in commands.keys():
        output = commands[f](args)  # Ejecucion de la instruccion
    else:
        print("Comando desconocido")
        output = "none"

    if output is "quit":
        out = True  # Salir del programa
    elif output != "none" and output != "ok":
        print(output)