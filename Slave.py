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

    def read(self, archivo):  # todo debería devolver únicamente los bloques que se requieren
        block_list = [self.database[i:i + self.memory]
                      for i in range(0, len(self.database), self.memoryBlock)]
        answer_list = [item[3:] for item in block_list if item[:2] == archivo]  # asume una clave de 4 caracteres
        return self.database

    def write(self, *args):  # todo en caso de no poderse escribir, no debería ni intentarlo
        aux = 1
        if not self.isFull():
            for argument in args:
                for item in argument:
                    self.database = self.database + item
            aux = 0
        return aux

    def isFull(self):
        if len(self.database) >= self.memory:
            return True
        else:
            return False

    def erase(self):  # todo debería borrar sólo lo que se pide
        block_list = [self.database[i:i + self.memory]
                      for i in range(0, len(self.database), self.memoryBlock)]
        return 0