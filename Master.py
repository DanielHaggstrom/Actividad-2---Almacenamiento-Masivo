import json

class Master:
    ############################################
    #               NO TOCAR                   #
    ############################################
    database = None        #Cadena de caracteres (STRING) que contiene toda la informacion del nodo maestro
    slaveDB = None         #Tupla de nodos esclavos
    memoryBlock = None     #Tamanyo del bloque de memoria actual, expresado en numero de caracteres

    def __init__(self, slaveDB, memoryBlock):
        self.database = json.dumps({"key_length": 5,
                                    "key_char": "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzÑñ",
                                    "file_dict": {'0': None, '1': None, '2': None, '3': None, '4': None, '5': None, '6': None, '7': None, '8': None, '9': None, 'A': None, 'B': None, 'C': None, 'D': None, 'E': None, 'F': None, 'G': None, 'H': None, 'I': None, 'J': None, 'K': None, 'L': None, 'M': None, 'N': None, 'O': None, 'P': None, 'Q': None, 'R': None, 'S': None, 'T': None, 'U': None, 'V': None, 'W': None, 'X': None, 'Y': None, 'Z': None, 'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None, 'i': None, 'j': None, 'k': None, 'l': None, 'm': None, 'n': None, 'o': None, 'p': None, 'q': None, 'r': None, 's': None, 't': None, 'u': None, 'v': None, 'w': None, 'x': None, 'y': None, 'z': None, 'Ñ': None, 'ñ': None},
                                    "mode": ["hasta_maxima_carga"]})
        self.slaveDB = slaveDB
        self.memoryBlock = memoryBlock

    ############################################
    #       MODIFICAR A PARTIR DE AQUI         #
    ############################################

    def get_next(self, string):
        # "suma 1" al string proporcionado
        var_dict = json.loads(self.database)
        key_char = var_dict["key_char"]
        new_s = ""
        if string != "z" * len(string):
            rev = string[::-1]
            new_s = ""
            aux = True
            for i in range(len(string)):
                char = key_char.find(rev[i])
                if not aux:
                    new_s += key_char[char]
                else:
                    if char != 63:
                        char = char + 1
                        new_s += key_char[char]
                        aux = False
                    else:
                        char = 0
                        new_s += key_char[char]
        return new_s[::-1]

    def get_key_from_file(self, value, dict):
        # dado un valor y un diccionario, devuelve la clave asignada a ese valor
        # presupone que los valores son únicos y que el valor existe en el diccionario
        for k, v in dict.items():
            if v == value:
                return k

    def read(self, arg):
        var_dict = json.loads(self.database)
        file_dict = var_dict["file_dict"]
        key_length = var_dict["key_length"]
        key_char = var_dict["key_char"]

        file = "".join(arg)
        # comprobamos si el archivo existe en el sistema
        if file not in file_dict.values():
            return "Ese archivo no está guardado en el sistema"
        key_file = self.get_key_from_file(file, file_dict)

        # pedimos a los nodos esclavos que nos den los bloques correspondientes
        block_list = []
        for slave in self.slaveDB.values():
            answer = slave.read(key_file, key_length, key_char)
            if len(answer) != 0:
                block_list.extend(answer)
        # ordenamos la lista
        block_list = sorted(block_list)

        # y la juntamos en un string, eliminando los metadatos
        texto = ""
        for item in block_list:
            texto = texto + item[key_length:]
        return texto

    def write(self, args):
        # divide el texto en bloques, les añade metadatos al principio y llama a la función adecuada según el modo
        # primero, comprobamos que el comando está bien escrito
        if len(args) != 2:
            return "Error de sintaxis. Use el comando 'ayuda' para más información."

        # cargamos las variables de nuestra base de datos
        var_dict = json.loads(self.database)
        mode_list = var_dict["mode"]
        file_dict = var_dict["file_dict"]
        key_char = var_dict["key_char"]
        key_length = var_dict["key_length"]

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
        if args[1] in file_dict.values():
            return "Error, ese texto ya está guardado"

        # comprobamos la cantidad de memoria
        # comprobamos que el número de archivos diferentes no es demasiado elevado
        if len([x for x in file_dict.values() if x is not None]) >= len(key_char):
            return "Error. Este simulador sólo puede almacenar " + str(len(key_char)) + " textos diferentes."

        texto = f.read()
        f.close()
        texto_length = len(texto)
        max_length = (len(key_char)**(key_length - 1)) * (self.slaveDB["S0"].memory - key_length)
        if texto_length > max_length:
            return "Error. El texto tiene " + str(texto_length) +\
                   " caracteres de longitud, este simulador acepta un máximo de " \
                   + str(max_length) + " caracteres por texto."
        memory_dict = {slave.id: slave.getFreeMemory(self.memoryBlock) for slave in self.slaveDB.values()}
        total_memory = sum(memory_dict.values()) * (self.memoryBlock - key_length)
        if texto_length > total_memory:
            return "Error de memoria. Necesita " \
                   + str((texto_length - total_memory)/((self.memoryBlock - key_length)*(self.slaveDB["S0"].memory/self.memoryBlock))) + " nodos más."

        # escogemos una clave para representar este archivo concreto
        key = ""
        for element in key_char:
            if file_dict[element] is None:
                key = element
                file_dict[key] = args[1]
                break

        # guardamos el nuevo file_dict
        var_dict["file_dict"] = file_dict
        self.database = json.dumps(var_dict)

        # dividimos el texto en bloques
        block_list = [texto[i:i+self.memoryBlock - key_length]
                      for i in range(0, len(texto), self.memoryBlock - key_length)]

        # añadimos los metadatos, que informan de a qué archivo pertenece cada bloque y en qué orden va
        count = "0" * (key_length - 2)
        for i in range(len(block_list)):
            block_list[i] = key + count + key_char[len(block_list[i]) + key_length] + block_list[i]
            count = self.get_next(count)

        # y es el turno de la función específica para el modo indicado.
        aux = False
        if mode == mode_list[0]:
            aux = self.maxima_carga(block_list)
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
        return True



    def erase(self, arg):
        # necesitamos file_dict
        var_dict = json.loads(self.database)
        file_dict = var_dict["file_dict"]
        key_char = var_dict["key_char"]
        key_length = var_dict["key_length"]
        file = "".join(arg)
        # comprobamos si el archivo existe en el sistema
        if file not in file_dict.values():
            return "Ese archivo no está guardado en el sistema"
        key_file = self.get_key_from_file(file, file_dict)
        sum_aux = 0
        for slave in self.slaveDB.values():
            if slave.database != "":
                sum_aux += slave.erase(key_file, key_length, key_char)
        if sum_aux == 0:
            file_dict[key_file] = None
            # guardamos el nuevo file_dict
            var_dict["file_dict"] = file_dict
            self.database = json.dumps(var_dict)
            return "Archivo borrado"
        else:
            return "Error en el borrado"

    def debug(self):
        for slave in self.slaveDB.values():
            if slave.database != "":
                print(slave.id + " " + slave.database)
