import random

class Slave:
    ############################################
    #               NO TOCAR                   #
    ############################################
    database = None        #Cadena de caracteres (STRING) que contiene toda la informacion del nodo esclavo
    id = None              #Nombre del nodo esclavo
    memory = None

    def __init__(self, id, maxMemory):
        self.database = ""
        self.id = id
        self.memory = maxMemory

    ############################################
    #       MODIFICAR A PARTIR DE AQUI         #
    ############################################

    def get_blocks(self, key_length, key_char):
        # devuelve una lista con los bloques contenidos en la base de datos
        block_list = []
        finished = False
        start = 0
        while not finished:
            end = key_char.find(self.database[start + key_length - 1]) + start
            block_list.append(self.database[start:end])
            start = end
            if start + key_length - 1 > len(self.database):
                finished = True
        return block_list


    def read(self, key_file, key_length, key_char):
        answer_list = []
        if self.database != "":
            block_list = self.get_blocks(key_length, key_char)
            answer_list = [block for block in block_list if block[0] == key_file]  # slave no elimina la clave
        return answer_list

    def write(self, texto, block_length):
        # devuelve 1 si no se logra ejecutar
        aux = 1
        if not self.isFull(block_length):
            self.database = self.database + texto
            aux = 0
        #p = 0.00000001
        p = 0.01
        if(random.random() < p ):
            self.database = ""
        return aux

    def isFull(self, block_length):
        # un nodo está  no lleno si tiene espacio para al menos un bloque más
        if len(self.database) + block_length > self.memory:
            return True
        else:
            return False

    def erase(self, key_file, key_length, key_char):
        # elimina los bloques que corresponden al archivo especificado
        if self.database != "":
            block_list = self.get_blocks(key_length, key_char)
            new_list = [block for block in block_list if block[0] != key_file]
            self.database = "".join(new_list)
        return 0

    def getFreeMemory(self, block_length):
        # devuelve el número de bloques que todavía entran en este nodo
        return (self.memory - len(self.database)) // block_length
