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

    def read(self, key_file, block_length):
        block_list = [self.database[i:i + block_length]
                      for i in range(0, len(self.database), block_length)]
        answer_list = [block for block in block_list if block[0] == key_file]  # slave no elimina la clave
        return answer_list

    def write(self, texto, block_length):
        # devuelve 1 si no se logra ejecutar
        aux = 1
        if not self.isFull(block_length):
            self.database = self.database + texto
            aux = 0
        return aux

    def isFull(self, block_length):
        # un nodo está  no lleno si tiene espacio para al menos un bloque más
        if len(self.database) + block_length > self.memory:
            return True
        else:
            return False

    def erase(self, key_file, block_length):
        # elimina los bloques que corresponden al archivo especificado
        block_list = [self.database[i:i + block_length]
                      for i in range(0, len(self.database), block_length)]
        new_list = [block for block in block_list if block[0] != key_file]
        self.database = "".join(new_list)
        return 0

    def getFreeMemory(self, block_length):
        # devuelve el número de bloques que todavía entran en este nodo
        return (self.memory - len(self.database)) // block_length
