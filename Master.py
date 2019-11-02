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

    # Definimos variables útiles
    file_list = []
    key_length = 4
    key_char = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzÑñ"
    # la "ñ" debe ir al final, ya que es así como python la ordena alfabéticamente
    mode = ["secuencial"]
    def __getNext(self, string):
        # "suma 1" al string proporcionado
        if string != "z" * len(string):
            rev = string[::-1]
            new_s = ""
            aux = True
            for i in range(len(string)):
                char = self.key_char.find(rev[i])
                if not aux:
                    new_s += self.key_char[char]
                else:
                    if char != 63:
                        char = char + 1
                        new_s += self.key_char[char]
                        aux = False
                    else:
                        char = 0
                        new_s += self.key_char[char]
        return(new_s[::-1])

    def read(self, arg):
        file = "".join(arg)
        # comprobamos si el archivo existe en el sistema
        if file not in self.file_list:
            return "Ese archivo no está guardado en el sistema"
        key_file = self.key_char[self.file_list.index(file)]

        # pedimos a los nodos esclavos que nos den los bloques correspondientes
        block_list = []
        for slave in self.slaveDB.values():
            answer = slave.read(key_file, self.memoryBlock)
            if len(answer) != 0:
                block_list.extend(answer)
        # ordenamos la lista
        block_list = sorted(block_list)

        # y la juntamos en un string, eliminando los metadatos
        texto = ""
        for item in block_list:
            texto = texto + item[self.key_length:]
        return texto

    def write(self, args):
        # divide el texto en bloques, les añade metadatos al principio y llama a la función adecuada según el modo
        # primero, comprobamos que el comando está bien escrito
        if len(args) != 2:
            return "Error de sintaxis. Use el comando 'ayuda' para más información."
        mode = args[0]
        if self.mode.count(mode) != 1:
            return "Error. El modo " + mode + " no existe. Use el comando 'ayuda' para más información."

        # ahora, abrimos el texto
        try:
            f = open(args[1])
        except:
            return "Error. No se encontró el archivo"

        # comprobamos que el archivo no haya sido guardado previamente
        if args[1] in self.file_list:
            return "Error, ese texto ya está guardado"

        # comprobamos la cantidad de memoria
        texto = f.read()
        f.close()
        texto_length = len(texto)
        print("debug texto_length = " + str(texto_length))  # todo quitar
        max_length = (len(self.key_char)**(self.key_length - 1)) * self.slaveDB["S0"].memory
        if texto_length > max_length:
            return "Error. El texto tiene " + str(texto_length) + " caracteres de longitud, este simulador acepta un máximo de " + str(max_length) + " caracteres por texto."
        memory_dict = {slave.id: slave.getFreeMemory(self.memoryBlock) for slave in self.slaveDB.values()}
        total_memory = sum(memory_dict.values())
        if texto_length/self.memoryBlock > total_memory:
            return "Error de memoria. El texto tiene " + str(texto_length) + " caracteres, necesita " + str(texto_length/self.slaveDB["S0"].memory) + " nodos."

        # comprobamos que el número de archivos diferentes no es demasiado elevado
        if len(self.file_list) >= len(self.key_char):
            return "Error. Este simulador sólo puede almacenar " + str(len(self.key_char)) + " textos diferentes."

        # escogemos una clave para representar este archivo concreto
        self.file_list.append(args[1])
        key = self.key_char[len(self.file_list) - 1]

        # dividimos el texto en bloques
        block_list = [texto[i:i+self.memoryBlock - self.key_length]
                      for i in range(0, len(texto), self.memoryBlock - self.key_length)]

        # añadimos los metadatos, que informan de a qué archivo pertenece cada bloque y en qué orden va
        count = "0" * (self.key_length - 1)
        for i in range(len(block_list)):
            block_list[i] = key + count + block_list[i]
            count = self.__getNext(count)

        # y es el turno de la función específica para el modo indicado.
        aux = False
        if mode == self.mode[0]:
            aux = self.sequential(block_list)
        if aux:
            return "Datos guardados."
        else:
            return "Error de escritura."

    def sequential(self, block_list):
        # escribe el archivo especificado de forma secuencial
        sum_aux = 0
        for slave in self.slaveDB.values():
            while not slave.isFull(self.memoryBlock) and len(block_list) > 0:
                sum_aux += slave.write(block_list[0], self.memoryBlock)
                block_list.pop(0)
        if sum_aux == 0:
            return True
        else:
            return False

    def erase(self, arg):
        file = "".join(arg)
        # comprobamos si el archivo existe en el sistema
        if file not in self.file_list:
            return "Ese archivo no está guardado en el sistema"
        key_file = self.key_char[self.file_list.index(file)]
        sum_aux = 0
        for slave in self.slaveDB.values():
            sum_aux += slave.erase(key_file, self.memoryBlock)
        if sum_aux == 0:
            self.file_list.remove(file)
            return "Archivo borrado"
        else:
            return "Error en el borrado"

    def debug(self):
        for slave in self.slaveDB.values():
            if slave.database != "":
                print(slave.id + " " + slave.database)
