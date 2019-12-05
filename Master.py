import random
import collections
import time

class Master:
    ############################################
    #               NO TOCAR                   #
    ############################################
    database = None  # Cadena de caracteres (STRING) que contiene toda la informacion del nodo maestro
    slaveDB = None  # Tupla de nodos esclavos
    memoryBlock = None  # Tamanyo del bloque de memoria actual, expresado en numero de caracteres

    def __init__(self, slaveDB, memoryBlock):
        self.database = ""
        self.slaveDB = slaveDB
        self.memoryBlock = memoryBlock

    ############################################
    #       MODIFICAR A PARTIR DE AQUI         #
    ############################################

    def get_key_length(self):
        return 6

    def get_key_char(self):
        return "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzÑñ"

    def get_file_list(self):
        var_list = self.database.split(" ")
        if len(var_list) > 2:
            return var_list[1::2]
        else:
            return []

    def get_key_from_file(self, file):
        file_list = self.get_file_list()
        key_list = self.get_key_list()
        return key_list[file_list.index(file)]


    def get_key_list(self):
        var_list = self.database.split(" ")
        if len(var_list) > 2:
            return var_list[2::2]
        else:
            return []

    def set_file_and_key_lists(self, file_list, key_list):
        s = ""
        list_tuple = zip(file_list, key_list)
        for file, key in list_tuple:
            s += " " + file + " " + key
        self.database = s

    def get_next(self, string):
        # "suma 1" al string proporcionado
        key_char = self.get_key_char()
        new_s = ""
        if string != key_char[-1] * len(string):
            rev = string[::-1]
            new_s = ""
            aux = True
            for i in range(len(string)):
                char = key_char.find(rev[i])
                if not aux:
                    new_s += key_char[char]
                else:
                    if char != len(key_char) - 1:
                        char = char + 1
                        new_s += key_char[char]
                        aux = False
                    else:
                        char = 0
                        new_s += key_char[char]
        return new_s[::-1]

    def read(self, arg):
        key_length = self.get_key_length()
        key_char = self.get_key_char()
        file_list = self.get_file_list()
        if len(file_list) == 0:
            return "No hay archivos guardados en el sistema."

        file = "".join(arg)
        # comprobamos si el archivo existe en el sistema
        if file not in file_list:
            return "Ese archivo no está guardado en el sistema."

        # obtenemos el identificador de archivo
        key_file = self.get_key_from_file(file)

        # pedimos a los nodos esclavos que nos den los bloques correspondientes
        block_list = []
        for slave in self.slaveDB.values():
            answer = slave.read(key_file, key_length, key_char)
            if len(answer) != 0:
                block_list.extend(answer)

        # ordenamos la lista
        block_list = sorted(block_list)

        # eliminamos los elementos repetidos
        new_block_list = list(dict.fromkeys(block_list))

        # y la juntamos en un string, eliminando los metadatos
        texto = ""
        for item in new_block_list:
            texto = texto + item[key_length:]
        return texto

    def write(self, args):
        # divide el texto en bloques, les añade metadatos al principio y llama a la función adecuada según el modo
        # primero, comprobamos que el comando está bien escrito
        if len(args) != 2:
            return "Error de sintaxis. Use el comando 'ayuda' para más información."

        # cargamos las variables de nuestra base de datos
        mode_list = ["hasta_maxima_carga", "a", "secuencial", "b", "aleatorio", "c", "primero_vacio", "d"]
        key_length = self.get_key_length()
        key_char = self.get_key_char()
        file_list = self.get_file_list()

        # comprobamos que el modo de escritura sea correcto
        mode = args[0]
        if mode_list.count(mode) != 1:
            return "Error. El modo " + mode + " no existe. Use el comando 'ayuda' para más información."

        # ahora, abrimos el texto
        try:
            f = open(args[1])
        except:
            return "Error. No se encontró el archivo"

        # comprobamos que el archivo no haya sido guardado previamente
        if args[1] in file_list:
            return "Error, ese texto ya está guardado"

        # comprobamos la cantidad de memoria
        # comprobamos que el número de archivos diferentes no es demasiado elevado
        if len(file_list) >= len(key_char):
            return "Error. Este simulador sólo puede almacenar " + str(len(key_char)) + " textos diferentes."

        texto = f.read()
        f.close()
        texto_length = len(texto)
        max_length = (len(key_char) ** (key_length - 1)) * (self.slaveDB["S0"].memory - key_length)
        if texto_length > max_length:
            return "Error. El texto tiene " + str(texto_length) + \
                   " caracteres de longitud, este simulador acepta un máximo de " \
                   + str(max_length) + " caracteres por texto."
        memory_dict = {slave.id: slave.getFreeMemory(self.memoryBlock) for slave in self.slaveDB.values()}
        total_memory = sum(memory_dict.values()) * (self.memoryBlock - key_length)
        if texto_length > total_memory:
            return "Error de memoria. Necesita " \
                   + str((texto_length - total_memory) / ((self.memoryBlock - key_length) * (
                        self.slaveDB["S0"].memory / self.memoryBlock))) + " nodos más."

        # escogemos una clave para representar este archivo concreto
        file_list.append(args[1])
        key_list = self.get_key_list()
        for char in key_char:
            if char not in key_list:
                key = char
                break
        key_list.append(key)

        # guardamos file_list y key_list
        self.set_file_and_key_lists(file_list, key_list)

        # dividimos el texto en bloques
        block_list = [texto[i:i + self.memoryBlock - key_length]
                      for i in range(0, len(texto), self.memoryBlock - key_length)]

        # añadimos los metadatos, que informan de a qué archivo pertenece cada bloque y en qué orden va
        count = key_char[0] * (key_length - 3)
        for i in range(len(block_list)):
            length_of_block = len(block_list[i]) + key_length
            current = key_char[0] * 2
            for j in range(length_of_block):
                current = self.get_next(current)

            block_list[i] = key + count + current + block_list[i]
            count = self.get_next(count)

        # y es el turno de la función específica para el modo indicado.
        aux = False
        rep_num = 3
        if mode in mode_list[0:2]:
            for i in range(rep_num):
                block_list_copy = block_list.copy()
                aux = self.maxima_carga(block_list_copy)
        elif mode in mode_list[2:4]:
            for i in range(rep_num):
                block_list_copy = block_list.copy()
                aux = self.secuencial(block_list_copy)
        elif mode in mode_list[4:6]:
            for i in range(rep_num):
                block_list_copy = block_list.copy()
                aux = self.aleatorio(block_list_copy)
        elif mode in mode_list[6:8]:
            for i in range(rep_num):
                block_list_copy = block_list.copy()
                aux = self.primero_vacio(block_list_copy, memory_dict)
        if aux:
            return "Datos guardados."
        else:
            return "Error de escritura."

    def maxima_carga(self, block_list):
        # escribe el archivo especificado nodo a nodo hasta la máxima carga
        sum_aux = 0
        for slave in self.slaveDB.values():
            while not slave.isFull(self.memoryBlock) and len(block_list) > 0:
                sum_aux += slave.write(block_list[0], self.memoryBlock)
                block_list.pop(0)
        if sum_aux == 0:
            return True
        else:
            return False

    def secuencial(self, block_list):
        # escribe datos de forma secuencial
        sum_aux = 0
        for slave in self.slaveDB.values():
            if not slave.isFull(self.memoryBlock):
                sum_aux += slave.write(block_list[0], self.memoryBlock)
                block_list.pop(0)
                if len(block_list) == 0:
                    break
        if sum_aux == 0:
            return True
        else:
            return False

    def aleatorio(self, block_list):
        # escribe datos en nodos aleatorios
        sum_aux = 0
        while len(block_list) > 0:
            slave_id = "S" + str(random.randint(0, len(self.slaveDB) - 1))
            slave = self.slaveDB[slave_id]
            if not slave.isFull(self.memoryBlock):
                sum_aux += slave.write(block_list[0], self.memoryBlock)
                block_list.pop(0)
        if sum_aux == 0:
            return True
        else:
            return False

    def primero_vacio(self, block_list, memory_dict):
        # escribe datos priorizando nodos vacíos
        sorted_by_second = sorted(memory_dict.items(), key=lambda tup: tup[1], reverse=True)
        slave_list = [tuple_of_memory[0] for tuple_of_memory in sorted_by_second]
        sum_aux = 0
        while len(block_list) > 0:
            for slave in slave_list:
                if not self.slaveDB[slave].isFull(self.memoryBlock):
                    sum_aux += self.slaveDB[slave].write(block_list[0], self.memoryBlock)
                    block_list.pop(0)
                    if len(block_list) == 0:
                        break
        if sum_aux == 0:
            return True
        else:
            return False

    def erase(self, arg):
        # necesitamos file_dict
        key_length = self.get_key_length()
        key_char = self.get_key_char()
        file_list = self.get_file_list()
        file = "".join(arg)

        # comprobamos si el archivo existe en el sistema
        if file not in file_list:
            return "Ese archivo no está guardado en el sistema"

        # obtenemos el identificador del archivo
        key_file = self.get_key_from_file(file)
        sum_aux = 0
        for slave in self.slaveDB.values():
            if slave.database != "":
                sum_aux += slave.erase(key_file, key_length, key_char)
        if sum_aux == 0:
            file_list.remove(file)
            key_list = self.get_key_list()
            key_list.remove(key_file)

            # guardamos los nuevos file_list y key_list
            self.set_file_and_key_lists(file_list, key_list)
            return "Archivo borrado"
        else:
            return "Error en el borrado"

    def debug(self):
        for slave in self.slaveDB.values():
            if slave.database != "":
                print(slave.id + " " + slave.database)
        print(self.database)

    def check_file(self, arg):
        key_length = self.get_key_length()
        key_char = self.get_key_char()
        file_list = self.get_file_list()
        if len(file_list) == 0:
            return "No hay archivos guardados en el sistema."

        file = "".join(arg)
        # comprobamos si el archivo existe en el sistema
        if file not in file_list:
            return "Ese archivo no está guardado en el sistema."

        # obtenemos el identificador de archivo
        key_file = self.get_key_from_file(file)

        # pedimos a los nodos esclavos que nos den los bloques correspondientes
        block_list = []
        for slave in self.slaveDB.values():
            answer = slave.read(key_file, key_length, key_char)
            if len(answer) != 0:
                block_list.extend(answer)

        counter = collections.Counter(block_list)
        # asumiremos rep_num = 3
        rep_num = 3
        sum = 0
        for key, value in counter.items():
            sum = sum + rep_num - value
        ratio = sum / len(block_list)
        return "El ratio de defectos es de " + str(ratio)
