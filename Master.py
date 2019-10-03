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
        texto = ""
        for slave in self.slaveDB.values():
            texto = texto + slave.database
        return texto

    def write(self, *args):
        self.erase()
        texto = ""
        for item in list(*args):
            texto = texto + " " + item
        texto = texto[1:]
        numSlaves = len(texto)//list(self.slaveDB.values())[0].memory +\
                    (len(texto) % list(self.slaveDB.values())[0].memory > 0)
        for c, i in enumerate(range(numSlaves)):
            start = c * self.slaveDB["S0"].memory
            end = start + self.slaveDB["S0"].memory
            self.slaveDB["S" + str(i)].write(texto[start:end])

    def erase(self):
        for slave in self.slaveDB.values():
            slave.database = ""