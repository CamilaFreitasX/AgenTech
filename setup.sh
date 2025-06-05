#!/bin/bash

# Instalar dependências
pip install -r requirements_google.txt

# Criar diretórios necessários se não existirem
mkdir -p ~/.streamlit/

# Configurar Streamlit
echo "\n[server]\n" > ~/.streamlit/config.toml
echo "headless = true\n" >> ~/.streamlit/config.toml
echo "port = $PORT\n" >> ~/.streamlit/config.toml
echo "enableCORS = false\n" >> ~/.streamlit/config.toml