# test_vector_store.py
import os
from dotenv import load_dotenv
from azure.ai.agents import AgentsClient
from azure.identity import DefaultAzureCredential

load_dotenv()

def test_vector_store_capabilities():
    """Testa as capacidades reais de Vector Store do AI Foundry"""
    try:
        endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
        model = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")
        
        client = AgentsClient(endpoint, DefaultAzureCredential())
        
        print("🔍 Explorando capacidades de Vector Store...")
        
        # 1. Verificar métodos disponíveis
        print("\n📋 Métodos de vector_stores:")
        vector_methods = [m for m in dir(client.vector_stores) if not m.startswith('_')]
        for method in vector_methods:
            print(f"  - {method}")
        
        # 2. Tentar criar Vector Store
        print("\n🧪 Testando criação de Vector Store...")
        vector_store = client.vector_stores.create(
            name="test-knowledge-base"
        )
        print(f"✅ Vector Store criado: {vector_store.id}")
        
        # 3. Verificar métodos de files no vector store
        print("\n📋 Métodos de vector_stores.files:")
        file_methods = [m for m in dir(client.vector_stores.files) if not m.startswith('_')]
        for method in file_methods:
            print(f"  - {method}")
        
        # 4. Testar upload de arquivo simples
        print("\n🧪 Testando upload de arquivo...")
        try:
            # Criar arquivo de teste
            test_content = "Este é um arquivo de teste para o Vector Store"
            with open("test_file.txt", "w", encoding='utf-8') as f:
                f.write(test_content)
            
            # Tentar upload
            with open("test_file.txt", "rb") as file:
                # Verificar método correto
                if hasattr(client.vector_stores.files, 'create'):
                    file_operation = client.vector_stores.files.create(
                        vector_store_id=vector_store.id,
                        file=file
                    )
                    print(f"✅ Arquivo enviado: {file_operation}")
                else:
                    print("❌ Método create não disponível em vector_stores.files")
            
            # Limpar arquivo de teste
            os.remove("test_file.txt")
            
        except Exception as e:
            print(f"❌ Erro no upload: {e}")
        
        # 5. Criar agent com Vector Store
        print("\n🧪 Testando criação de agent com Vector Store...")
        agent = client.create_agent(
            model=model,
            instructions="Test agent with vector store",
            tools=[{
                "type": "file_search",
                "vector_store_ids": [vector_store.id]
            }]
        )
        print(f"✅ Agent criado com Vector Store: {agent.id}")
        
        # Limpeza
        client.delete_agent(agent.id)
        client.vector_stores.delete(vector_store.id)
        print("✅ Recursos limpos")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

if __name__ == "__main__":
    test_vector_store_capabilities()