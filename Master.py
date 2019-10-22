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
        block_lists = []
        for slave in self.slaveDB.values():
            print(slave.read("1", self.memoryBlock))
            block_lists.append(slave.read("1", self.memoryBlock))
        # se ordena la lista. En nuestro caso, no hace falta
        # se junta en un string, eliminando los metadatos
        texto = ""
        for list in block_lists:
            for item in list:
                texto = texto + item[1:]
        return texto

    def write(self, args):
        # divide el texto en bloques de tamaño memoryBlock - clave,
        # les añade la clave y los escribe en los nodos esclavos
        texto = ' '.join(args)
        clave_length = 1  # la clave define el número de archivo. De momento, lo hardcodeamos a 1
        block_list = [texto[i:i+self.memoryBlock - clave_length]
                      for i in range(0, len(texto), self.memoryBlock - clave_length)]
        # todo debería comprobar si hay espacio para realizar la operacion
        result = "Datos guardados"
        # rellenamos el último bloque con espacios
        if len(block_list[-1]) + clave_length < self.memoryBlock:
            dif = self.memoryBlock - len(block_list[-1]) - clave_length
            padding = " " * dif
            block_list[-1] = block_list[-1] + padding
        for slave in self.slaveDB.values():
            while not slave.isFull() and len(block_list) > 0:
                slave.write("1" + block_list[0])  # clave hardcodeada, "1"
                block_list.pop(0)
        return result

    def erase(self, archivo):
        # todo borrar los bloques del archivo especificado
        return None
