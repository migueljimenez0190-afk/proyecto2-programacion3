# GraphLab · Proyecto 3

Autor: Miguel Jimenez

Aplicación web de una red de transporte dirigida, desarrollada con Streamlit
sobre el motor de grafos y la persistencia CSV del Proyecto 2.

## Funcionalidad

- Cálculo de rutas mínimas con Dijkstra: origen, destino, recorrido y costo.
- Registro de conexiones con pesos finitos no negativos.
- Persistencia de cada conexión en nodos.csv y actualización del grafo en RAM.
- Tabla de conexiones con Pandas y visualización de la red dirigida.

## Arquitectura

- app.py: interfaz con pestañas, formulario y controles de texto.
- grafo.py: clases Nodo y Grafo, y algoritmo de Dijkstra.
- io_handler.py: validación, lectura y escritura CSV.
- main.py: interfaz de consola del Proyecto 2.
- nodos.csv: seis conexiones de ejemplo.
- test_graphlab.py: pruebas funcionales y de integración.

El grafo se inicializa una sola vez por sesión mediante st.session_state.
La tabla y el dibujo se construyen desde RAM. La persistencia precede a la
actualización en memoria. En conexiones repetidas prevalece el último peso.
Cada sesión mantiene su propio estado; los cambios externos se reflejan al
iniciar una sesión nueva.

Los errores de entrada y de archivos se comunican mediante alertas visuales.
Las filas inválidas del CSV se omiten con advertencias. Un archivo inexistente
inicia una red vacía. Los fallos de lectura por permisos, codificación o E/S
bloquean la escritura en esa sesión.

## Validación

Entorno de pruebas: Python 3.12.14 y Streamlit 1.67.0.
Análisis de estilo: Flake8, sin errores.
Pruebas automatizadas: 16 aprobadas con pytest y Streamlit AppTest.
Las pruebas utilizan archivos temporales y conservan el CSV de ejemplo.
La carpeta evidencia contiene la salida de validación y capturas de escritorio.

Caso de referencia: A → C → D → E, costo mínimo 7.
