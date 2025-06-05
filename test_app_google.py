#!/usr/bin/env python3
"""
Script de teste para criar dados de exemplo - versão Google Gemini
"""

import pandas as pd
import numpy as np
import os
import zipfile
from datetime import datetime, timedelta
import random

def generate_sample_data():
    """Gera dados de exemplo de notas fiscais"""
    print("📊 Gerando dados de exemplo...")
    
    # Configurações
    num_notas = 100
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 31)
    
    # Listas de dados realistas
    fornecedores = [
        ("12.345.678/0001-90", "Tech Solutions Ltda"),
        ("98.765.432/0001-10", "Suprimentos Industriais S.A."),
        ("11.222.333/0001-44", "Materiais de Escritório Express"),
        ("55.666.777/0001-88", "Equipamentos Profissionais Ltda"),
        ("33.444.555/0001-22", "Distribuidora Nacional"),
        ("77.888.999/0001-66", "Produtos Especializados S.A."),
        ("22.333.444/0001-77", "Fornecedor Premium Ltda"),
        ("44.555.666/0001-33", "Comercial Regional"),
        ("66.777.888/0001-99", "Atacado Empresarial"),
        ("99.000.111/0001-55", "Indústria Moderna S.A.")
    ]
    
    produtos = [
        ("COMP001", "Computador Desktop Core i7", "UN", 2500.00),
        ("MON001", "Monitor LED 24 polegadas", "UN", 800.00),
        ("TEC001", "Teclado Mecânico", "UN", 350.00),
        ("MOU001", "Mouse Óptico", "UN", 80.00),
        ("CAB001", "Cabo HDMI", "UN", 45.00),
        ("IMP001", "Impressora Multifuncional", "UN", 1200.00),
        ("PAP001", "Papel A4 500 folhas", "PCT", 25.00),
        ("TON001", "Toner para Impressora", "UN", 180.00),
        ("CAD001", "Cadeira Ergonômica", "UN", 750.00),
        ("MES001", "Mesa para Escritório", "UN", 950.00),
        ("ARM001", "Armário de Aço", "UN", 1100.00),
        ("LUM001", "Luminária LED", "UN", 120.00),
        ("EXT001", "Extintor de Incêndio", "UN", 85.00),
        ("CAM001", "Câmera de Segurança", "UN", 320.00),
        ("ROT001", "Roteador Wi-Fi", "UN", 280.00)
    ]
    
    # Gera dados de cabeçalho
    cabecalho_data = []
    
    for i in range(1, num_notas + 1):
        cnpj, nome = random.choice(fornecedores)
        data_emissao = start_date + timedelta(
            days=random.randint(0, (end_date - start_date).days),
            hours=random.randint(8, 18),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )
        
        # Valores base
        valor_produtos = round(random.uniform(500, 10000), 2)
        desconto = round(valor_produtos * random.uniform(0, 0.1), 2)
        acrescimo = round(valor_produtos * random.uniform(0, 0.05), 2)
        valor_total = round(valor_produtos - desconto + acrescimo, 2)
        
        cabecalho_data.append({
            'numero': f"{i:06d}",
            'serie': random.choice(['001', '002', '003']),
            'data_emissao': data_emissao.strftime('%Y-%m-%d %H:%M:%S'),
            'cnpj_fornecedor': cnpj,
            'nome_fornecedor': nome,
            'valor_produtos': valor_produtos,
            'desconto': desconto,
            'acrescimo': acrescimo,
            'valor_total': valor_total,
            'situacao': random.choice(['Normal', 'Cancelada', 'Autorizada']),
            'observacoes': f"Nota fiscal {i:06d} - Compra de materiais"
        })
    
    # Gera dados de itens
    itens_data = []
    item_id = 1
    
    for nota in cabecalho_data:
        num_itens = random.randint(1, 8)  # 1 a 8 itens por nota
        valor_restante = nota['valor_produtos']
        
        for j in range(num_itens):
            codigo, descricao, unidade, preco_base = random.choice(produtos)
            
            if j == num_itens - 1:  # Último item ajusta para fechar o valor
                quantidade = max(1, int(valor_restante / preco_base))
                valor_unitario = round(valor_restante / quantidade, 2) if quantidade > 0 else preco_base
                valor_item = valor_restante
            else:
                quantidade = random.randint(1, 10)
                # Varia o preço unitário em ±20%
                fator_variacao = random.uniform(0.8, 1.2)
                valor_unitario = round(preco_base * fator_variacao, 2)
                valor_item = round(quantidade * valor_unitario, 2)
                
                # Garante que não exceda o valor restante
                if valor_item > valor_restante:
                    valor_item = valor_restante
                    valor_unitario = round(valor_item / quantidade, 2)
                
                valor_restante -= valor_item
            
            itens_data.append({
                'numero_nf': nota['numero'],
                'item': f"{j+1:03d}",
                'codigo_produto': codigo,
                'descricao': descricao,
                'quantidade': quantidade,
                'unidade': unidade,
                'valor_unitario': valor_unitario,
                'valor_total': valor_item,
                'ncm': f"{random.randint(1000, 9999)}.{random.randint(10, 99)}.{random.randint(10, 99)}",
                'cfop': random.choice(['5102', '6102', '5403', '6403', '5949']),
                'origem': random.choice(['0', '1', '2']),
                'cst': random.choice(['000', '010', '020', '030'])
            })
            
            item_id += 1
            
            if valor_restante <= 0:
                break
    
    # Cria DataFrames
    df_cabecalho = pd.DataFrame(cabecalho_data)
    df_itens = pd.DataFrame(itens_data)
    
    print(f"✅ Gerados {len(df_cabecalho)} cabeçalhos e {len(df_itens)} itens")
    
    return df_cabecalho, df_itens

def save_csv_files(df_cabecalho, df_itens):
    """Salva os DataFrames como arquivos CSV"""
    print("💾 Salvando arquivos CSV...")
    
    # Cria diretório de exemplo se não existir
    os.makedirs("exemplo_dados", exist_ok=True)
    
    # Salva os arquivos
    cabecalho_path = "exemplo_dados/202401_NFs_Cabecalho.csv"
    itens_path = "exemplo_dados/202401_NFs_Itens.csv"
    
    df_cabecalho.to_csv(cabecalho_path, index=False, encoding='utf-8')
    df_itens.to_csv(itens_path, index=False, encoding='utf-8')
    
    print(f"✅ Arquivo de cabeçalho salvo: {cabecalho_path}")
    print(f"✅ Arquivo de itens salvo: {itens_path}")
    
    return cabecalho_path, itens_path

def create_zip_file(cabecalho_path, itens_path):
    """Cria arquivo ZIP com os CSVs"""
    print("📦 Criando arquivo ZIP...")
    
    zip_path = "exemplo_dados/notas_fiscais_exemplo.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(cabecalho_path, "202401_NFs_Cabecalho.csv")
        zipf.write(itens_path, "202401_NFs_Itens.csv")
    
    print(f"✅ Arquivo ZIP criado: {zip_path}")
    return zip_path

def show_data_summary(df_cabecalho, df_itens):
    """Mostra resumo dos dados gerados"""
    print("\n" + "="*50)
    print("📊 RESUMO DOS DADOS GERADOS")
    print("="*50)
    
    print(f"\n📄 CABEÇALHO:")
    print(f"   - Total de notas: {len(df_cabecalho)}")
    print(f"   - Período: {df_cabecalho['data_emissao'].min()} a {df_cabecalho['data_emissao'].max()}")
    print(f"   - Valor total geral: R$ {df_cabecalho['valor_total'].sum():,.2f}")
    print(f"   - Fornecedores únicos: {df_cabecalho['nome_fornecedor'].nunique()}")
    
    print(f"\n📦 ITENS:")
    print(f"   - Total de itens: {len(df_itens)}")
    print(f"   - Produtos únicos: {df_itens['codigo_produto'].nunique()}")
    print(f"   - Quantidade total: {df_itens['quantidade'].sum():,}")
    
    print(f"\n🏆 TOP 5 FORNECEDORES POR VALOR:")
    top_fornecedores = df_cabecalho.groupby('nome_fornecedor')['valor_total'].sum().sort_values(ascending=False).head()
    for i, (fornecedor, valor) in enumerate(top_fornecedores.items(), 1):
        print(f"   {i}. {fornecedor}: R$ {valor:,.2f}")
    
    print(f"\n🛍️ TOP 5 PRODUTOS POR QUANTIDADE:")
    top_produtos = df_itens.groupby('descricao')['quantidade'].sum().sort_values(ascending=False).head()
    for i, (produto, qtd) in enumerate(top_produtos.items(), 1):
        print(f"   {i}. {produto}: {qtd:,} unidades")
    
    print("\n" + "="*50)

def test_google_api():
    """Testa a conexão com Google Gemini (opcional)"""
    print("\n🧪 Teste opcional da Google Gemini API...")
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        import os
        
        # Tenta carregar API key
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key and os.path.exists(".env"):
            with open(".env", "r") as f:
                for line in f:
                    if line.startswith("GOOGLE_API_KEY="):
                        api_key = line.split("=", 1)[1].strip()
                        break
        
        if not api_key:
            print("⚠️  Google API Key não encontrada - teste pulado")
            return False
        
        # Testa o modelo
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.1
        )
        
        response = llm.invoke("Responda apenas 'OK' se você está funcionando")
        print(f"✅ Google Gemini respondeu: {response.content}")
        return True
        
    except Exception as e:
        print(f"⚠️  Erro no teste da API: {e}")
        return False

def main():
    """Função principal"""
    print("🤖 GERADOR DE DADOS DE EXEMPLO - Google Gemini")
    print("="*60)
    
    try:
        # Gera os dados
        df_cabecalho, df_itens = generate_sample_data()
        
        # Salva os arquivos
        cabecalho_path, itens_path = save_csv_files(df_cabecalho, df_itens)
        
        # Cria arquivo ZIP
        zip_path = create_zip_file(cabecalho_path, itens_path)
        
        # Mostra resumo
        show_data_summary(df_cabecalho, df_itens)
        
        # Teste opcional da API
        test_google_api()
        
        print("\n🎉 Dados de exemplo criados com sucesso!")
        print(f"📁 Use o arquivo {zip_path} para testar a aplicação")
        print("\n💡 Para executar a aplicação:")
        print("   streamlit run main_google.py")
        
    except Exception as e:
        print(f"❌ Erro ao gerar dados: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()