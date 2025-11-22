import asyncio
import os
import inspect
from dotenv import load_dotenv

load_dotenv()

async def explore_agents_client():
    """Explora os métodos disponíveis no AgentsClient"""
    from azure.ai.agents.aio import AgentsClient
    from azure.identity.aio import DefaultAzureCredential
    
    endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    
    if not endpoint:
        print("❌ AZURE_AI_PROJECT_ENDPOINT não configurado")
        return
    
    print("🔍 Explorando AgentsClient...")
    
    async with DefaultAzureCredential() as credential:
        async with AgentsClient(endpoint=endpoint, credential=credential) as client:
            print("\n📋 MÉTODOS DISPONÍVEIS NO AgentsClient:")
            methods = [method for method in dir(client) if not method.startswith('_')]
            for method in sorted(methods):
                print(f"  - {method}")
            
            print("\n📋 ATRIBUTOS DISPONÍVEIS NO AgentsClient:")
            attributes = [attr for attr in dir(client) if not callable(getattr(client, attr)) and not attr.startswith('_')]
            for attr in sorted(attributes):
                print(f"  - {attr}")
            
            # Explorar vector_stores se disponível
            if hasattr(client, 'vector_stores'):
                print("\n🔍 Explorando vector_stores...")
                vector_stores = client.vector_stores
                vector_methods = [method for method in dir(vector_stores) if not method.startswith('_')]
                for method in sorted(vector_methods):
                    print(f"  - vector_stores.{method}")

async def explore_alternative_clients():
    """Explora outros clients possíveis"""
    print("\n🔍 Tentando importar AIProjectClient...")
    try:
        from azure.ai.projects.aio import AIProjectClient
        from azure.identity.aio import DefaultAzureCredential
        
        endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
        
        async with DefaultAzureCredential() as credential:
            async with AIProjectClient(endpoint=endpoint, credential=credential) as client:
                print("✅ AIProjectClient importado com sucesso!")
                print("\n📋 MÉTODOS DISPONÍVEIS NO AIProjectClient:")
                methods = [method for method in dir(client) if not method.startswith('_')]
                for method in sorted(methods):
                    print(f"  - {method}")
                
                # Explorar agents se disponível
                if hasattr(client, 'agents'):
                    print("\n🔍 Explorando agents...")
                    agents = client.agents
                    agent_methods = [method for method in dir(agents) if not method.startswith('_')]
                    for method in sorted(agent_methods):
                        print(f"  - agents.{method}")
                        
    except ImportError as e:
        print(f"❌ AIProjectClient não disponível: {e}")

async def test_vector_store_operations():
    """Testa operações específicas de Vector Store"""
    from azure.ai.agents.aio import AgentsClient
    from azure.identity.aio import DefaultAzureCredential
    
    endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    
    print("\n🔍 Testando operações de Vector Store...")
    
    async with DefaultAzureCredential() as credential:
        async with AgentsClient(endpoint=endpoint, credential=credential) as client:
            if hasattr(client, 'vector_stores'):
                vs_client = client.vector_stores
                
                # Listar métodos específicos
                print("Métodos de vector_stores:")
                methods = [method for method in dir(vs_client) if not method.startswith('_')]
                for method in sorted(methods):
                    print(f"  - {method}")
                    
                # Testar criação de vector store
                try:
                    print("\n🧪 Testando criação de Vector Store...")
                    vector_store = await vs_client.create(name="test-exploration")
                    print(f"✅ Vector Store criado: {vector_store.id}")
                    
                    # Explorar métodos de upload
                    print("\n🔍 Explorando métodos de upload...")
                    # Verificar se há métodos específicos para arquivos
                    file_methods = [method for method in dir(vs_client) if 'file' in method.lower()]
                    for method in file_methods:
                        print(f"  - {method}")
                    
                    # Limpar
                    await vs_client.delete(vector_store.id)
                    print("✅ Vector Store removido")
                    
                except Exception as e:
                    print(f"❌ Erro ao testar Vector Store: {e}")

async def main():
    print("=== EXPLORAÇÃO DA API AZURE AI FOUNDRY ===")
    
    await explore_agents_client()
    await explore_alternative_clients()
    await test_vector_store_operations()

if __name__ == "__main__":
    asyncio.run(main())