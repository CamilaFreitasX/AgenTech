#!/usr/bin/env python3
"""
Script de instalação para o Agente de Análise de Notas Fiscais com Google Gemini
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def print_header():
    """Exibe cabeçalho do instalador"""
    print("="*60)
    print("🤖 INSTALADOR - AGENTE DE ANÁLISE DE NOTAS FISCAIS")
    print("📊 Powered by Google Gemini API & LangChain")
    print("="*60)
    print()

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    print("🔍 Verificando versão do Python...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ é necessário. Versão atual:", sys.version)
        return False
    
    print(f"✅ Python {sys.version.split()[0]} detectado")
    return True

def check_pip():
    """Verifica se pip está disponível"""
    print("🔍 Verificando pip...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        print("✅ pip disponível")
        return True
    except subprocess.CalledProcessError:
        print("❌ pip não encontrado")
        return False

def install_requirements():
    """Instala as dependências necessárias"""
    print("📦 Instalando dependências...")
    
    requirements = [
        "streamlit>=1.28.0",
        "pandas>=1.5.0",
        "langchain>=0.1.0",
        "langchain-experimental>=0.0.50",
        "langchain-google-genai>=1.0.0",
        "google-genai>=0.5.0",
        "python-dotenv>=1.0.0",
        "openpyxl>=3.1.0",
        "requests>=2.31.0",
        "numpy>=1.24.0"
    ]
    
    for package in requirements:
        try:
            print(f"   Instalando {package}...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], check=True, capture_output=True)
            print(f"   ✅ {package} instalado")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Erro ao instalar {package}")
            print(f"   Erro: {e}")
            return False
    
    print("✅ Todas as dependências instaladas com sucesso!")
    return True

def setup_google_api_key():
    """Configura a Google API Key"""
    print("🔑 Configuração da Google API Key...")
    print()
    
    # Verifica se já existe no ambiente
    if os.getenv("GOOGLE_API_KEY"):
        print("✅ Google API Key já configurada nas variáveis de ambiente")
        return True
    
    # Verifica se existe arquivo .env
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            content = f.read()
            if "GOOGLE_API_KEY=" in content:
                print("✅ Google API Key encontrada no arquivo .env")
                return True
    
    print("Para usar a aplicação, você precisa de uma Google API Key.")
    print("📝 Como obter sua Google API Key:")
    print("   1. Acesse https://ai.google.dev/")
    print("   2. Faça login com sua conta Google")
    print("   3. Clique em 'Get API Key in Google AI Studio'")
    print("   4. Crie uma nova API Key")
    print("   5. Copie a chave gerada")
    print()
    
    while True:
        choice = input("Deseja configurar a API Key agora? (s/n): ").lower().strip()
        if choice in ['s', 'sim', 'y', 'yes']:
            break
        elif choice in ['n', 'não', 'nao', 'no']:
            print("⚠️  Você pode configurar a API Key depois no arquivo .env")
            return True
        else:
            print("Por favor, digite 's' para sim ou 'n' para não")
    
    api_key = input("Cole sua Google API Key aqui: ").strip()
    
    if not api_key:
        print("⚠️  Nenhuma API Key fornecida. Configure depois no arquivo .env")
        return True
    
    # Cria arquivo .env
    env_content = f"""# Google API Configuration
GOOGLE_API_KEY={api_key}

# Opcional: Configurações do modelo
GEMINI_MODEL=gemini-1.5-flash
GEMINI_TEMPERATURE=0.1

# Configurações da aplicação
APP_TITLE=Agente de Análise de Notas Fiscais
APP_ICON=📊
"""
    
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ API Key salva no arquivo .env")
        
        # Define também como variável de ambiente para a sessão atual
        os.environ["GOOGLE_API_KEY"] = api_key
        
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar API Key: {e}")
        return False

def test_api_connection():
    """Testa a conexão com a API do Google"""
    print("🧪 Testando conexão com Google Gemini API...")
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        # Tenta carregar API key
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key and os.path.exists(".env"):
            with open(".env", "r") as f:
                for line in f:
                    if line.startswith("GOOGLE_API_KEY="):
                        api_key = line.split("=", 1)[1].strip()
                        break
        
        if not api_key:
            print("⚠️  API Key não encontrada. Configure no arquivo .env")
            return False
        
        # Testa o modelo
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.1
        )
        
        # Faz uma consulta simples
        response = llm.invoke("Hello, test connection")
        
        if response:
            print("✅ Conexão com Google Gemini API bem-sucedida!")
            return True
        else:
            print("❌ Erro na resposta da API")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar API: {e}")
        print("   Verifique se sua API Key está correta")
        return False

def create_sample_data():
    """Pergunta se deseja criar dados de exemplo"""
    print("📊 Dados de Exemplo...")
    print()
    
    while True:
        choice = input("Deseja criar dados de exemplo para testar? (s/n): ").lower().strip()
        if choice in ['s', 'sim', 'y', 'yes']:
            break
        elif choice in ['n', 'não', 'nao', 'no']:
            return True
        else:
            print("Por favor, digite 's' para sim ou 'n' para não")
    
    try:
        # Executa o script de teste
        subprocess.run([sys.executable, "test_app_google.py"], check=True)
        print("✅ Dados de exemplo criados com sucesso!")
        return True
    except subprocess.CalledProcessError:
        print("⚠️  Script de dados de exemplo não encontrado")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar dados de exemplo: {e}")
        return False

def show_usage_instructions():
    """Mostra instruções de uso"""
    print("="*60)
    print("🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*60)
    print()
    print("📋 Para executar a aplicação:")
    print("   streamlit run main_google.py")
    print()
    print("🌐 A aplicação abrirá no navegador em:")
    print("   http://localhost:8501")
    print()
    print("📁 Arquivos importantes:")
    print("   - main_google.py: Aplicação principal")
    print("   - utils_google.py: Utilitários")
    print("   - .env: Configurações (inclui API Key)")
    print("   - requirements_google.txt: Dependências")
    print()
    print("🔑 Google Gemini API:")
    print("   - 1.5 bilhão de tokens gratuitos por dia")
    print("   - 15 requisições por minuto (tier gratuito)")
    print("   - Modelos avançados disponíveis")
    print()
    print("📚 Documentação:")
    print("   - Google AI Studio: https://ai.google.dev/")
    print("   - LangChain: https://python.langchain.com/")
    print("   - Streamlit: https://docs.streamlit.io/")
    print()
    print("⚠️  Lembre-se de manter sua API Key segura!")
    print("="*60)

def main():
    """Função principal do instalador"""
    print_header()
    
    # Verificações
    if not check_python_version():
        sys.exit(1)
    
    if not check_pip():
        sys.exit(1)
    
    # Instalação
    if not install_requirements():
        print("❌ Falha na instalação das dependências")
        sys.exit(1)
    
    # Configuração da API
    if not setup_google_api_key():
        print("❌ Falha na configuração da API Key")
        sys.exit(1)
    
    # Teste da API
    if not test_api_connection():
        print("⚠️  Não foi possível testar a conexão com a API")
        print("   Você pode testar manualmente executando a aplicação")
    
    # Dados de exemplo
    create_sample_data()
    
    # Instruções finais
    show_usage_instructions()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Instalação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)