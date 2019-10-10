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

    def read(self):
        return self.database

    def write(self, *args):
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

    def erase(self):
        self.database = ""
        return 0
