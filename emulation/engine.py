# emulation/engine.py

# =================================================================
# Tarea 5.1: Implementar las Clases del Sistema de Archivos
# =================================================================

class VirtualNode:
    """Clase base para todos los objetos en nuestro sistema de archivos virtual."""

    def __init__(self, name, owner='root', group='root', permissions='rwxr-xr-x'):
        self.name = name
        self.owner = owner
        self.group = group
        self.permissions = permissions
        self.size_bytes = 0

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.name}')"


class VirtualFile(VirtualNode):
    """Representa un archivo. Hereda de VirtualNode."""

    def __init__(self, name, content="", **kwargs):
        super().__init__(name, **kwargs)
        self.content = content
        self.permissions = '-' + self.permissions[1:]
        self.size_bytes = len(content.encode('utf-8'))


class VirtualDirectory(VirtualNode):
    """Representa un directorio. Hereda de VirtualNode."""

    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.children = {}
        self.permissions = 'd' + self.permissions[1:]
        self.size_bytes = 4096  # Tamaño base de un directorio

    def add_child(self, node):
        """Añade un nodo (archivo o directorio) a este directorio."""
        self.children[node.name] = node

    def get_child(self, name):
        """Busca y devuelve un nodo hijo por su nombre."""
        return self.children.get(name)

    def list_children(self):
        """Devuelve una lista de los nombres de los nodos hijos."""
        return sorted(self.children.keys())


# =================================================================
# Tarea 5.4 (parcial): Clases de Discos y Particiones
# =================================================================

class VirtualDisk:
    """Representa un disco físico virtual."""

    def __init__(self, name, size_bytes):
        self.name = name
        self.size = size_bytes


class VirtualPartition(VirtualDisk):
    """Representa una partición dentro de un disco."""

    def __init__(self, name, size_bytes, mount_point, filesystem_type='ext4'):
        super().__init__(name, size_bytes)
        self.mount_point = mount_point
        self.filesystem_type = filesystem_type
        self.used_space = 0  # Se calculará dinámicamente.


# =================================================================
# Clase Principal del Motor de Emulación
# =================================================================

class EmulationEngine:
    """
    Gestiona el estado completo del mundo virtual (VFS, particiones)
    y provee la API interna para que la IA interactúe con él.
    """

    def __init__(self):
        # Tarea 5.3: Poblar el "Arbol Base" al iniciar.
        self.vfs_root, self.partitions = self._create_initial_world()
        print("Motor de Emulación inicializado con el Arbol Base.")
        # Tarea 5.4 (parcial): Calcular el uso inicial del disco.
        self.update_disk_usage()

    def _create_initial_world(self):
        """Crea el estado inicial del VFS y las particiones."""
        # Definir Particiones
        partitions = {
            '/': VirtualPartition(name='/dev/sda1', size_bytes=50 * 1024 ** 3, mount_point='/'),
            '/home': VirtualPartition(name='/dev/sda3', size_bytes=100 * 1024 ** 3, mount_point='/home'),
            '/var': VirtualPartition(name='/dev/sda4', size_bytes=100 * 1024 ** 3, mount_point='/var'),
        }
        # Construir VFS
        root = VirtualDirectory('/')
        root.add_child(VirtualDirectory('home'))
        root.add_child(VirtualDirectory('var'))
        root.add_child(VirtualDirectory('etc'))
        root.add_child(VirtualDirectory('usr'))

        # Añadir subdirectorios y archivos
        root.get_child('var').add_child(VirtualDirectory('log'))
        root.get_child('var').get_child('log').add_child(
            VirtualFile('syslog', content='Aug 2 02:50:00 server boot: System started.'))
        root.get_child('home').add_child(VirtualDirectory('admin'))
        root.get_child('home').get_child('admin').add_child(VirtualFile('readme.txt', content='Welcome to EvaluaTIC'))
        root.get_child('etc').add_child(VirtualFile('hosts', content='127.0.0.1 localhost'))

        return root, partitions

    def _navigate_to_path(self, path):
        """Función auxiliar para encontrar un nodo en el VFS a partir de una ruta."""
        if not path.startswith('/'):
            return None  # Solo soportamos rutas absolutas por ahora

        parts = path.strip('/').split('/')
        current_node = self.vfs_root

        if path == '/':
            return current_node

        for part in parts:
            if isinstance(current_node, VirtualDirectory) and part in current_node.children:
                current_node = current_node.get_child(part)
            else:
                return None  # Ruta no encontrada
        return current_node

    # =================================================================
    # Tarea 5.2: Implementar los "Command Handlers" Básicos
    # =================================================================
    def _emulate_ls(self, path):
        """Lógica para listar el contenido de un directorio en el VFS."""
        node = self._navigate_to_path(path)
        if isinstance(node, VirtualDirectory):
            return node.list_children()
        elif isinstance(node, VirtualFile):
            return [node.name]  # Si es un archivo, solo lista el archivo mismo
        else:
            return f"Error: No se puede acceder a '{path}': No existe el fichero o el directorio"

    def _emulate_mkdir(self, path):
        """Lógica para crear un nuevo directorio en el VFS."""
        parent_path = '/'.join(path.strip('/').split('/')[:-1])
        new_dir_name = path.strip('/').split('/')[-1]

        # Corregir para la raíz
        parent_path = '/' + parent_path if parent_path else '/'

        parent_node = self._navigate_to_path(parent_path)

        if isinstance(parent_node, VirtualDirectory):
            if new_dir_name in parent_node.children:
                return f"Error: No se puede crear el directorio '{path}': El fichero ya existe"
            new_dir = VirtualDirectory(new_dir_name)
            parent_node.add_child(new_dir)
            return f"Directorio '{new_dir_name}' creado."
        else:
            return f"Error: La ruta '{parent_path}' no es válida."

    def _emulate_touch(self, path):
        """Lógica para crear un nuevo archivo vacío en el VFS."""
        parent_path = '/'.join(path.strip('/').split('/')[:-1])
        new_file_name = path.strip('/').split('/')[-1]

        parent_path = '/' + parent_path if parent_path else '/'

        parent_node = self._navigate_to_path(parent_path)

        if isinstance(parent_node, VirtualDirectory):
            if new_file_name in parent_node.children:
                # Si el archivo existe, solo actualizamos su "fecha", por ahora no hacemos nada.
                return ""
            new_file = VirtualFile(new_file_name)
            parent_node.add_child(new_file)
            return f"Archivo '{new_file_name}' creado."
        else:
            return f"Error: La ruta '{parent_path}' no es válida."

    # =================================================================
    # Tarea 5.4 (final): Implementar la Simulación de Discos
    # =================================================================
    def _calculate_dir_size(self, directory_node):
        """Función recursiva para calcular el tamaño total de un directorio."""
        total_size = directory_node.size_bytes
        for child in directory_node.children.values():
            if isinstance(child, VirtualDirectory):
                total_size += self._calculate_dir_size(child)
            else:
                total_size += child.size_bytes
        return total_size

    def update_disk_usage(self):
        """Recorre el VFS, suma el tamaño de los archivos y asigna el uso a cada partición."""
        # Reiniciar todos los contadores
        for p in self.partitions.values():
            p.used_space = 0

        # Calcular el tamaño de cada directorio de primer nivel (puntos de montaje)
        for mount_point, partition in self.partitions.items():
            if mount_point == '/': continue  # La raíz se maneja al final

            node = self._navigate_to_path(mount_point)
            if node:
                partition.used_space = self._calculate_dir_size(node)

        # Calcular el tamaño de la raíz (sin incluir otros puntos de montaje)
        root_size = self.vfs_root.size_bytes
        for child_name, child_node in self.vfs_root.children.items():
            # Si el hijo NO es un punto de montaje, sumamos su tamaño al de la raíz.
            if f'/{child_name}' not in self.partitions:
                if isinstance(child_node, VirtualDirectory):
                    root_size += self._calculate_dir_size(child_node)
                else:
                    root_size += child_node.size_bytes
        self.partitions['/'].used_space = root_size

    def get_disk_usage(self):
        """Devuelve un diccionario con el estado actual de los discos."""
        self.update_disk_usage()  # Asegurarse de que los datos estén actualizados
        usage_dict = {}
        for mount_point, p in self.partitions.items():
            usage_dict[mount_point] = {
                'name': p.name,
                'total_gb': round(p.size / 1024 ** 3, 2),
                'used_gb': round(p.used_space / 1024 ** 3, 2)
            }
        return usage_dict
