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

    def read(self, clave, memoryBlock):
        block_list = [self.database[i:i + self.memory]
                      for i in range(0, len(self.database), memoryBlock)]
        answer_list = [block for block in block_list if block[0] == clave]  # slave no elimina la clave
        return answer_list

    def write(self, texto):
        # devuelve 1 si no se logra ejecutar
        aux = 1
        if not self.isFull():
            self.database = self.database + texto
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