import random
import collections


class Master:
    ############################################
    #               NO TOCAR                   #
    ############################################
    database = None  # Cadena de caracteres (STRING) que contiene toda la informacion del nodo maestro
    slaveDB = None  # Tupla de nodos esclavos
    memoryBlock = None  # Tamanyo del bloque de memoria actual, expresado en numero de caracteres

    def __init__(self, slaveDB, memoryBlock):
        self.database = "0"
        self.slaveDB = slaveDB
        self.memoryBlock = memoryBlock

    ############################################
    #       MODIFICAR A PARTIR DE AQUI         #
    ############################################

    def get_key_length(self):
        return 6

    def get_time_since_check(self):
        var_list = self.database.split(" ")
        return var_list[0]

    def get_key_char(self):
        return "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzÑñ"

    def get_file_list(self):
        var_list = self.database.split(" ")
        if len(var_list) > 2:
            return var_list[1::3]
        else:
            return []

    def get_key_from_file(self, file):
        file_list = self.get_file_list()
        key_list = self.get_key_list()
        return key_list[file_list.index(file)]

    def get_key_list(self):
        var_list = self.database.split(" ")
        if len(var_list) > 2:
            return var_list[2::3]
        else:
            return []

    def get_rep_dict(self):
        # a diferencia de file y key, los elementos no son únicos, por eso devolveremos un diccionario {key: rep}
        var_list = self.database.split(" ")
        if len(var_list) > 2:
            keys = self.get_key_list()
            values = var_list[3::3]
            return dict(zip(keys, values))
        else:
            return {}

    def reset_time(self):
        self.update_metadata("0", self.get_file_list(), self.get_key_list(), self.get_rep_dict())

    def update_metadata(self, integrity_count, file_list, key_list, rep_dict):
        s = integrity_count
        rep_list = [rep_dict[item] for item in key_list]
        list_tuple = zip(file_list, key_list, rep_list)
        for file, key, rep in list_tuple:
            s += " " + file + " " + key + " " + str(rep)
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
        if len(args) != 3:
            return "Error de sintaxis. Use el comando 'ayuda' para más información."

        # cargamos las variables de nuestra base de datos
        mode_list = ["hasta_maxima_carga", "a", "secuencial", "b", "aleatorio", "c", "primero_vacio", "d"]
        key_length = self.get_key_length()
        key_char = self.get_key_char()
        file_list = self.get_file_list()
        rep_dict = self.get_rep_dict()

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

        # comprobamos que rep_num sea correcto
        rep_num = int(args[2]) + 1
        if rep_num <= 0:
            return "El número de réplicas no puede ser negativo"

        # comprobamos la cantidad de memoria
        # comprobamos que el número de archivos diferentes no es demasiado elevado
        if len(file_list) >= len(key_char):
            return "Error. Este simulador sólo puede almacenar " + str(len(key_char)) + " textos diferentes."

        texto = f.read()
        f.close()
        texto_length = len(texto) * rep_num
        max_length = (len(key_char) ** (key_length - 3)) * (self.slaveDB["S0"].memory - key_length)
        if texto_length > max_length:
            return "Error. El texto (junto con sus réplicas) tiene " + str(texto_length) + \
                   " caracteres de longitud, este simulador acepta un máximo de " \
                   + str(max_length) + " caracteres por texto."
        memory_dict = {slave.id: slave.getFreeMemory(self.memoryBlock) for slave in self.slaveDB.values()}
        total_memory = sum(memory_dict.values()) * (self.memoryBlock - key_length)
        if texto_length > total_memory:
            return "Error de memoria. Necesita " \
                   + str((texto_length - total_memory) / ((self.memoryBlock - key_length) * (self.slaveDB["S0"].memory / self.memoryBlock))) + " nodos más."

        # escogemos una clave para representar este archivo concreto
        file_list.append(args[1])
        key_list = self.get_key_list()
        for char in key_char:
            if char not in key_list:
                key = char
                break
        key_list.append(key)
        rep_dict[key] = rep_num

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
            # guardamos file_list, key_list y rep_dict
            time_since = self.get_time_since_check()
            self.update_metadata(str(int(time_since) + rep_num), file_list, key_list, rep_dict)

            # comprobamos la integridad
            if int(int(time_since) + rep_num) > 9:
                print("Han pasado " + str(int(time_since) + rep_num) + " operaciones de escritura desde la última comprobación de integridad. Se recomienda que use el comando 'comprobar'.")
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

    def rewrite(self):
        # borra y reescribe todos los archivos, en modo secuencial
        file_list = self.get_file_list()
        rep_dict = self.get_rep_dict()
        rep_list = [rep_dict[self.get_key_from_file(file)] for file in file_list]
        for file in file_list:
            self.erase((file,))
        for file, rep in tuple(zip(file_list, rep_list)):
            self.write(("a", file, rep))
        self.reset_time()
        return "Sistema restablecido."

    def erase(self, arg):
        # necesitamos metadatos
        key_length = self.get_key_length()
        key_char = self.get_key_char()
        file_list = self.get_file_list()
        rep_dict = self.get_rep_dict()
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
            rep_dict.pop(key_file)

            # guardamos los nuevos file_list, key_list y rep_dict
            if len(file_list) == 0:
                # si no hay archivos guardados, reseteamos el tiempo desde el último restablecimiento
                self.update_metadata(0, file_list, key_list, rep_dict)
            else:
                self.update_metadata(self.get_time_since_check(), file_list, key_list, rep_dict)
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
        rep_dict = self.get_rep_dict()
        rep_num = int(rep_dict[key_file])
        sum = 0
        for key, value in counter.items():
            sum = sum + rep_num - value
        ratio = sum / len(block_list)
        return str(ratio)

    def check_all(self):
        file_list = self.get_file_list()
        for file in file_list:
            print("El ratio de defectos de " + file + " es " + self.check_file(file))

    @staticmethod
    def char_count(database):
        frequency = {}
        for char in database:
            if char in frequency:
                frequency[char] = frequency[char] + 1
            else:
                frequency[char] = 1
        return list(frequency.items())

    @staticmethod
    def pair_count(database):
        # si el texto tiene longitud impar, ignoramos el último carácter
        if len(database) % 2 != 0:
            database = database[:-1]
        pairs = [database[i:i+2] for i in range(0, len(database))]
        frequency = {}
        for pair in pairs:
            if pair in frequency:
                frequency[pair] = frequency[pair] + 1
            else:
                frequency[pair] = 1
        return list(frequency.items())

    @staticmethod
    def word_show(database):
        frequency = {}
        words = database.split()
        for word in words:
            if word[-1] == ".":
                word = word[:-1]
            if word in frequency:
                frequency[word] = frequency[word] + 1
            else:
                frequency[word] = 1
        return list(frequency.items())

    def mapReduce(self, mode, arg):
        list_of_maps = []
        char_dict = {}
        file_list = self.get_file_list()
        if len(file_list) == 0:
            return "No hay archivos guardados en el sistema."

        file = "".join(arg)
        # comprobamos si el archivo existe en el sistema
        if file not in file_list:
            return "Ese archivo no está guardado en el sistema."

        # obtenemos el identificador de archivo
        key_file = self.get_key_from_file(file)

        # obtenemos una lista de tuplas clave-valor (una tupla por nodo)
        for slave in self.slaveDB.values():
            if slave.database != "":
                if mode == 0:
                    list_of_maps.append(
                        slave.map(self.char_count, self.get_key_length(), self.get_key_char(), key_file))
                elif mode == 1:
                    list_of_maps.append(
                        slave.map(self.pair_count, self.get_key_length(), self.get_key_char(), key_file))
                elif mode == 2:
                    list_of_maps.append(
                        slave.map(self.word_show, self.get_key_length(), self.get_key_char(), key_file))

        # obtenemos un diccionario que asocia a cada clave una lista de valores
        for element in list_of_maps:
            for item in element:
                if item[0] in char_dict:
                    char_dict[item[0]].append(item[1])
                else:
                    char_dict[item[0]] = [item[1]]

        # pasamos a cada esclavo una clave y su lista
        result = {}
        for key in char_dict.keys():
            slave = self.slaveDB["S" + str(random.randint(0, len(self.slaveDB) - 1))]
            result.update(slave.reduce(key, char_dict[key]))

        # dividimos por el número de réplicas
        rep_num = int(self.get_rep_dict()[key_file])
        result = {k: v//rep_num for k, v in result.items()}

        # si se ha pedido word_show, todavía queda trabajo por hacer
        if mode != 2:
            return result
        words = [word for word, amount in result.items() if amount == 1]
        words.sort(key=len, reverse=True)
        return words



