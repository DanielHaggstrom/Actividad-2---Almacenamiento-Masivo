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

    # ESTAMOS TRABAJANDO BAJO LA SUPOSICION CASO 1: SECUENCIA

    def read(self, *args):
        st = ""
        for slave in self.slaveDB.values():
            st = st + slave.database
        return st

    def write(self, *args):
        for c, slave in enumerate(list(self.slaveDB.values())):
            start = c * slave.memory
            end = start + slave.memory
            slave.write(*args[start:end])

    def erase(self):
        self.write("")