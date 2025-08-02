class LearnedCommand:
    def __init__(self, name):
        self.name = name
        self.synopsis = ""
        self.description = ""
        self.options = {} # Diccionario para opciones como -l, -a
        self.action_mapping = "" # La acción a ejecutar, ej. "list_directory"