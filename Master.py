class Master:
    ############################################
    #               NO TOCAR                   #
    ############################################
    database = None        #Cadena de caracteres (STRING) que contiene toda la informacion del nodo maestro
    slaveDB = None         #Tupla de nodos esclavos
    memoryBlock = None     #Tamanyo del bloque de memoria actual, expresado en numero de caracteres

    def __init__(self, slaveDB, memoryBlock):
        self.database = ""
        self.slaveDB = slaveDB
        self.memoryBlock = memoryBlock

    ############################################
    #       MODIFICAR A PARTIR DE AQUI         #
    ############################################

    # ESTAMOS TRABAJANDO BAJO LA SUPOSICION CASO 1: SECUENCIAL

    def read(self, *args):
        texto = ""
        for slave in self.slaveDB.values():
            texto = texto + slave.read()
        return texto

    def write(self, texto):
        for slave in self.slaveDB.values():
            while not slave.isFull() and len(texto) > 0:
                slave.write(texto[0])
                texto = texto[1:]

    def erase(self):
        for slave in self.slaveDB.values():
            slave.erase()

    def isFull(self):
        if len(self.database) >= self.memoryBlock:
            return True
        else:
            return False
