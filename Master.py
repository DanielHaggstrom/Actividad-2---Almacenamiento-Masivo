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

    # TRABAJAMOS BAJO EL CASO 1: SECUENCIAL

    def read(self, archivo):
        # pide a los nodos esclavos que le den los bloques correspondientes, y los ordena, y los junta, y lo devuelve
        block_list = []
        for slave in self.slaveDB.values():
            block_list.append(slave.read(archivo))
        # todo ordenar la lista, eliminando los metadatos
        texto = ""
        for item in block_list:
            texto = texto + item
        return texto

    def write(self, archivo, texto):
        # divide el texto en bloques de tamaño memoryBlock - clave,
        # les añade la clave y los escribe en los nodos esclavos
        clave_length = 4
        block_list = [texto[i:i+self.memoryBlock - clave_length]
                      for i in range(0, len(texto), self.memoryBlock - clave_length)]
        # todo sumar la clave en cada bloque
        # todo escribir en slave
        return None

    def erase(self, archivo):
        # todo borrar los bloques del archivo especificado
        return None
