#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import zipfile
import os
import tempfile
from io import StringIO

# Tente este import alternativo:
try:
    from langchain_experimental.agents import create_csv_agent
except ImportError:
    from langchain.agents import create_csv_agent

from langchain_openai import ChatOpenAI
from langchain.agents.agent_types import AgentType
from utils_openai import NotaFiscalValidator, extract_zip_file
import warnings
from dotenv import load_dotenv

load_dotenv()

import streamlit as st
import warnings
warnings.filterwarnings("ignore")

class CSVAnalysisAgent:
    def __init__(self, openai_api_key=None):
        """Inicializa o agente de análise CSV com OpenAI GPT"""
        self.openai_api_key = openai_api_key
        self.agents = {}
        self.dataframes = {}
        self.file_info = {}
        
    def create_llm(self):
        """Cria uma instância do modelo OpenAI GPT"""
        if not self.openai_api_key:
            raise ValueError("OpenAI API Key é necessária para usar o agente")
        
        try:
            llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                openai_api_key=self.openai_api_key,
                temperature=0.1
            )
            return llm
        except Exception as e:
            st.error(f"Erro ao criar modelo GPT: {str(e)}")
            return None

    def load_csv_data(self, file_path, file_type):
        """Carrega dados CSV e cria agente específico"""
        try:
            # Lê o arquivo CSV
            df = pd.read_csv(file_path, encoding='utf-8')
            
            # Armazena o dataframe
            self.dataframes[file_type] = df
            self.file_info[file_type] = {
                'path': file_path,
                'shape': df.shape,
                'columns': df.columns.tolist()
            }
            
            # Cria o LLM
            llm = self.create_llm()
            if llm is None:
                return False
            
            # Cria agente específico para este CSV
            agent = create_csv_agent(
                llm,
                file_path,
                verbose=True,
                agent_type=AgentType.OPENAI_FUNCTIONS,
                allow_dangerous_code=True,
                handle_parsing_errors=True
            )
            
            self.agents[file_type] = agent
            return True
            
        except Exception as e:
            st.error(f"Erro ao carregar arquivo {file_type}: {str(e)}")
            return False

    def create_general_agent(self):
        """Cria um agente geral que pode acessar todos os dataframes"""
        try:
            if not self.dataframes:
                print("Erro: Nenhum dataframe carregado")
                return None
            
            llm = self.create_llm()
            if llm is None:
                print("Erro: Não foi possível criar LLM")
                return None
            
            # Coleta TODOS os caminhos de arquivos válidos usando file_info
            file_paths = []
            for file_type, info in self.file_info.items():
                if 'path' in info and os.path.exists(info['path']):
                    file_paths.append(info['path'])
            
            if not file_paths:
                print("Erro: Nenhum arquivo válido encontrado")
                return None
            
            print(f"Criando agente geral com {len(file_paths)} arquivo(s): {file_paths}")
            
            # Cria agente geral com todos os arquivos
            general_agent = create_csv_agent(
                llm,
                file_paths,
                verbose=True,
                agent_type=AgentType.OPENAI_FUNCTIONS,
                allow_dangerous_code=True,
                handle_parsing_errors=True
            )
            
            return general_agent
            
        except Exception as e:
            print(f"Erro ao criar agente geral: {str(e)}")
            st.error(f"Erro ao criar agente geral: {str(e)}")
            return None

    def query(self, question, use_general_agent=True):
        """Executa uma consulta usando o agente apropriado"""
        try:
            if use_general_agent:
                agent = self.create_general_agent()
                if agent is None:
                    return "Erro: Não foi possível criar o agente geral."
            else:
                # Usa o primeiro agente disponível se não usar o geral
                if not self.agents:
                    return "Erro: Nenhum agente disponível."
                agent = list(self.agents.values())[0]
            
            # Adiciona contexto sobre os dados
            context = self._build_context()
            full_question = f"{context}\n\nPergunta: {question}"
            
            # Executa a consulta
            response = agent.run(full_question)
            return response
            
        except Exception as e:
            error_msg = f"Erro ao processar consulta: {str(e)}"
            print(error_msg)
            return error_msg
    
    def _build_context(self):
        """Constrói contexto sobre os dados carregados"""
        context_parts = []
        context_parts.append("Você é um assistente especializado em análise de notas fiscais.")
        context_parts.append("Responda sempre em português brasileiro.")
        context_parts.append("Seja preciso e forneça exemplos quando possível.")
        context_parts.append("\nDados disponíveis:")
        
        for file_type, info in self.file_info.items():
            context_parts.append(f"- {file_type.title()}: {info['shape'][0]} registros, {info['shape'][1]} colunas")
            context_parts.append(f"  Colunas: {', '.join(info['columns'][:5])}{'...' if len(info['columns']) > 5 else ''}")
        
        return "\n".join(context_parts)

def main():
    # Configuração da página
    st.set_page_config(
        page_title="AgenTech - Análise de Notas Fiscais com GPT",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Título principal
    st.title("🤖 AgenTech - Análise Inteligente de Notas Fiscais")
    st.markdown("### 📊 Powered by OpenAI GPT & LangChain")
    
    # Sidebar para configurações
    st.sidebar.header("⚙️ Configurações")
    
    # Verificação da API Key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_api_key:
        st.sidebar.error("🔑 OpenAI API Key não encontrada!")
        st.sidebar.markdown("""
        **Como configurar:**
        1. Obtenha sua API Key em: https://platform.openai.com/api-keys
        2. Crie um arquivo `.env` na raiz do projeto
        3. Adicione: `OPENAI_API_KEY=sua_api_key_aqui`
        """)
        st.stop()
    else:
        st.sidebar.success("🔑 OpenAI API Key configurada!")
    
    # Inicialização do agente
    if 'agent' not in st.session_state:
        st.session_state.agent = CSVAnalysisAgent(openai_api_key)
    
    # Upload de arquivos
    st.sidebar.markdown("---")
    st.sidebar.header("📁 Upload de Arquivos")
    
    uploaded_files = st.sidebar.file_uploader(
        "Escolha arquivos CSV ou ZIP",
        type=['csv', 'zip'],
        accept_multiple_files=True,
        help="Faça upload de arquivos CSV de notas fiscais ou arquivos ZIP contendo CSVs"
    )
    
    # Processamento dos arquivos
    if uploaded_files:
        validator = NotaFiscalValidator()
        
        with st.spinner("🔄 Processando arquivos..."):
            for uploaded_file in uploaded_files:
                # Salva arquivo temporário
                with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                try:
                    if uploaded_file.name.endswith('.zip'):
                        # Processa arquivo ZIP
                        temp_dir = extract_zip_file(uploaded_file)  # Passa o objeto uploaded_file, não tmp_path
                        
                        if temp_dir:  # Verifica se a extração foi bem-sucedida
                            # Lista os arquivos CSV no diretório extraído
                            csv_files = [f for f in os.listdir(temp_dir) if f.endswith('.csv')]
                            
                            for csv_file in csv_files:
                                csv_path = os.path.join(temp_dir, csv_file)
                                file_type = validator.identify_file_type(csv_path)
                                if file_type != 'unknown':
                                    success = st.session_state.agent.load_csv_data(csv_path, file_type)
                                    if success:
                                        st.sidebar.success(f"✅ {file_type.title()} carregado!")
                                    else:
                                        st.sidebar.error(f"❌ Erro ao carregar {file_type}")
                        else:
                            st.sidebar.error("❌ Erro ao extrair arquivo ZIP")
                    
                    elif uploaded_file.name.endswith('.csv'):
                        # Processa arquivo CSV
                        file_type = validator.identify_file_type(tmp_path)
                        if file_type != 'unknown':
                            success = st.session_state.agent.load_csv_data(tmp_path, file_type)
                            if success:
                                st.sidebar.success(f"✅ {file_type.title()} carregado!")
                            else:
                                st.sidebar.error(f"❌ Erro ao carregar {file_type}")
                        else:
                            st.sidebar.warning(f"⚠️ Tipo de arquivo não identificado: {uploaded_file.name}")
                
                except Exception as e:
                    st.sidebar.error(f"❌ Erro ao processar {uploaded_file.name}: {str(e)}")
                
                finally:
                    # Limpa arquivo temporário
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
    
    # Exibição dos dados carregados
    if st.session_state.agent.dataframes:
        st.markdown("---")
        st.header("📊 Dados Carregados")
        
        # Tabs para diferentes tipos de dados
        tabs = st.tabs([f"{file_type.title()} ({info['shape'][0]} registros)" 
                       for file_type, info in st.session_state.agent.file_info.items()])
        
        for i, (file_type, df) in enumerate(st.session_state.agent.dataframes.items()):
            with tabs[i]:
                st.dataframe(df.head(10), use_container_width=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Registros", df.shape[0])
                with col2:
                    st.metric("Colunas", df.shape[1])
                with col3:
                    if 'valor_total' in df.columns:
                        total_value = df['valor_total'].sum() if pd.api.types.is_numeric_dtype(df['valor_total']) else 0
                        st.metric("Valor Total", f"R$ {total_value:,.2f}")
    
    # Interface de consulta
    st.markdown("---")
    st.header("💬 Faça sua Pergunta")
    
    if st.session_state.agent.dataframes:
        # Exemplos de perguntas
        st.markdown("**💡 Exemplos de perguntas:**")
        examples = [
            "Qual o valor total das notas fiscais?",
            "Quantas notas fiscais foram emitidas?",
            "Quais são os principais fornecedores?",
            "Qual o produto mais vendido?",
            "Mostre um resumo dos dados por mês"
        ]
        
        cols = st.columns(len(examples))
        for i, example in enumerate(examples):
            if cols[i].button(example, key=f"example_{i}"):
                st.session_state.user_question = example
        
        # Campo de entrada
        user_question = st.text_area(
            "Digite sua pergunta sobre os dados:",
            value=st.session_state.get('user_question', ''),
            height=100,
            placeholder="Ex: Qual o valor total das notas fiscais do mês de janeiro?"
        )
        
        # Botão de consulta
        if st.button("🔍 Analisar", type="primary"):
            if user_question.strip():
                with st.spinner("🤖 Analisando dados com GPT..."):
                    try:
                        response = st.session_state.agent.query(user_question)
                        
                        # Limpa e exibe a resposta
                        if response and str(response).strip():
                            # Remove possíveis prefixos de debug
                            clean_response = str(response).strip()
                            
                            # Remove linhas que começam com "Tipo da resposta" ou similar
                            lines = clean_response.split('\n')
                            clean_lines = []
                            for line in lines:
                                if not any(debug_prefix in line.lower() for debug_prefix in 
                                         ['tipo da resposta', 'conteúdo da resposta', 'debug:', '===']):
                                    clean_lines.append(line)
                            
                            final_response = '\n'.join(clean_lines).strip()
                            
                            # Exibe a resposta final
                            st.markdown(final_response)
                        else:
                            st.error("Não foi possível obter uma resposta válida.")
                    except Exception as e:
                        st.error(f"Erro ao processar pergunta: {str(e)}")
            else:
                st.warning("⚠️ Por favor, digite uma pergunta.")
    else:
        st.info("📁 Faça upload de arquivos CSV ou ZIP para começar a análise.")
    
    # Informações adicionais
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📚 Sobre")
    st.sidebar.markdown("""
    Esta aplicação utiliza:
    - **OpenAI GPT** para processamento de linguagem natural
    - **LangChain** para criação de agentes inteligentes
    - **Streamlit** para interface web
    - **Pandas** para manipulação de dados
    """)
    
    st.sidebar.markdown("### 🔗 Links Úteis")
    st.sidebar.markdown("""
    - [OpenAI Platform](https://platform.openai.com/)
    - [LangChain Documentation](https://python.langchain.com/)
    - [Streamlit Documentation](https://docs.streamlit.io/)
    """)

if __name__ == "__main__":
    main()