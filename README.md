# Proyecto 2 - Programación III
## Red de Transporte con Dijkstra

### Descripción
Programa modular en Python para registrar conexiones entre
nodos de una red de transporte, guardar los datos en un
archivo CSV y calcular rutas de menor costo usando Dijkstra.

### Archivos
- main.py: Menú interactivo.
- grafo.py: Clases Nodo, Grafo y algoritmo Dijkstra.
- io_handler.py: Lectura, escritura y validación del CSV.
- nodos.csv: Almacena las conexiones de la red.
- requirements.txt: Dependencia Flake8.

### Requisitos
- Python 3
- Flake8 para revisar el código.

### Instalación
python3 -m pip install -r requirements.txt

### Ejecución
python3 main.py

### Opciones del menú
1. Agregar conexión: Solicita origen, destino y peso.
2. Consultar ruta: Calcula el camino de menor costo.
3. Mostrar conexiones: Muestra los nodos y sus conexiones.
4. Salir: Finaliza el programa.

### Archivo CSV
Los registros se guardan en nodos.csv con la estructura:

Origen,Destino,Peso
A,B,4.0
A,C,2.0

Las conexiones son dirigidas y los pesos deben ser
números finitos mayores o iguales a cero.

### Manejo de errores
El programa utiliza try-except para controlar entradas
inválidas y errores durante el procesamiento de datos.
Las filas corruptas del CSV se omiten durante la carga.

### Verificación de estilo
flake8 main.py grafo.py io_handler.py
