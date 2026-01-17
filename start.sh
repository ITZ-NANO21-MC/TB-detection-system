#!/bin/bash

# Activar el entorno virtual
source /home/nano/Documentos/env/bin/activate

# Configurar el path para encontrar el paquete 'app'
export PYTHONPATH=.

# Iniciar la aplicación
echo "Iniciando Sistema de Detección de TB..."
python3 run.py
