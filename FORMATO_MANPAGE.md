# Guía de Formato para Man Pages (.txt) de EvaluaTIC

## 1. Propósito

Este documento define el estándar de formato para todos los archivos de texto (`.txt`) ubicados en la carpeta `manpages`. El cumplimiento de este estándar es **crítico** para que el motor de la IA pueda procesar (parsear) la información de manera correcta y aprender a emular los comandos de forma fiable.

## 2. Estructura General

-   **Codificación:** Todos los archivos deben guardarse con codificación **UTF-8**.
-   **Secciones:** El contenido de cada manual se divide en secciones. Cada sección comienza con un encabezado en mayúsculas.

## 3. Secciones Obligatorias

Estas secciones **deben estar presentes** en cada archivo para que la IA pueda aprender la función básica del comando.

### NOMBRE
-   Describe el nombre y la función principal del comando en una sola línea.
-   **Formato:** `nombre_comando - descripción breve y en minúsculas.`

### SINOPSIS
-   Describe la sintaxis del comando, incluyendo opciones y argumentos.
-   **Formato:** `nombre_comando [OPCION]... [ARGUMENTO]...`

### DESCRIPCIÓN
-   Contiene una explicación más detallada de lo que hace el comando.
-   **Crítico para la IA:** Esta sección debe contener las **palabras clave** que el motor de la IA buscará para mapear el comando a una acción emulada (ej. "lista el contenido", "crea directorios", "elimina ficheros").

## 4. Secciones Opcionales

Estas secciones añaden contexto y detalle, enriqueciendo la información que se muestra al usuario, pero no son críticas para la lógica de emulación básica.

-   `OPCIONES`
-   `EJEMPLOS`
-   `AUTOR`
-   `VER TAMBIÉN`

## 5. Reglas de Formato Estrictas

1.  **Encabezados de Sección:**
    -   Deben estar siempre en **MAYÚSCULAS**.
    -   Deben estar al inicio de una línea, sin espacios antes.
    -   Deben ser la única palabra en esa línea.

2.  **Contenido de Sección:**
    -   El texto que describe una sección debe comenzar en la línea **inmediatamente después** del encabezado.
    -   Todo el contenido de una sección debe tener una **sangría (indentación) de 4 espacios**. Esto es fundamental para que el parser separe visualmente los encabezados del contenido.

3.  **Formato de Opciones:**
    -   Dentro de la sección `OPCIONES`, cada opción debe comenzar con su bandera (ej. `-l, --long`) y tener una sangría adicional para mayor claridad.

## 6. Ejemplo Completo (`ls.txt`)

El siguiente es un ejemplo de un archivo `ls.txt` formateado correctamente:

```
NOMBRE
    ls - lista el contenido de un directorio

SINOPSIS
    ls [OPCION]... [FICHERO]...

DESCRIPCIÓN
    Lista información sobre los FICHEROS (el directorio actual por defecto).
    Esta descripción contiene las palabras clave que la IA usará para aprender
    la acción 'list_directory'.

OPCIONES
    -l
        Usa un formato de lista larga.
    -a, --all
        No oculta las entradas que empiezan con .
    -h, --human-readable
        Con -l, imprime tamaños en formato legible.
```