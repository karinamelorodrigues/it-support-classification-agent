import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def explore_upload_methods():
    """Explora os métodos disponíveis para upload de arquivos"""
    from azure.ai.agents.aio import AgentsClient
    from azure.identity.aio import DefaultAzureCredential
    
    endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    
    print("🔍 Explorando métodos de upload...")
    
    async with DefaultAzureCredential() as credential:
        async with AgentsClient(endpoint=endpoint, credential=credential) as client:
            # Explorar vector_store_files
            print("\n📋 MÉTODOS DISPONÍVEIS EM vector_store_files:")
            if hasattr(client, 'vector_store_files'):
                vs_files = client.vector_store_files
                methods = [method for method in dir(vs_files) if not method.startswith('_')]
                for method in sorted(methods):
                    print(f"  - vector_store_files.{method}")
                    
                    # Verificar assinatura dos métodos principais
                    if method in ['create', 'create_and_poll']:
                        try:
                            method_obj = getattr(vs_files, method)
                            print(f"    Assinatura: {method_obj}")
                        except:
                            pass
            
            # Explorar files
            print("\n📋 MÉTODOS DISPONÍVEIS EM files:")
            if hasattr(client, 'files'):
                files_client = client.files
                methods = [method for method in dir(files_client) if not method.startswith('_')]
                for method in sorted(methods):
                    print(f"  - files.{method}")
            
            # Testar criação de vector store
            print("\n🧪 Testando criação de Vector Store...")
            try:
                vector_store = await client.vector_stores.create(name="test-upload")
                print(f"✅ Vector Store criado: {vector_store.id}")
                
                # Testar diferentes métodos de upload
                test_file_path = "./knowledge_base/support_procedures.json"
                if os.path.exists(test_file_path):
                    print(f"\n🧪 Testando upload do arquivo: {test_file_path}")
                    
                    # Método 1: Tentar com vector_store_files.create
                    try:
                        with open(test_file_path, 'rb') as f:
                            file_content = f.read()
                        
                        print("📤 Tentando vector_store_files.create...")
                        result = await client.vector_store_files.create(
                            vector_store_id=vector_store.id,
                            file=file_content
                        )
                        print(f"✅ Sucesso: {result}")
                    except Exception as e1:
                        print(f"❌ Falha método 1: {e1}")
                    
                    # Método 2: Tentar com files.create primeiro
                    try:
                        print("📤 Tentando files.create + vector_store_files.create...")
                        with open(test_file_path, 'rb') as f:
                            file_obj = await client.files.create(
                                file=f,
                                purpose="assistants"
                            )
                        print(f"✅ Arquivo criado: {file_obj.id}")
                        
                        # Associar ao vector store
                        vs_file = await client.vector_store_files.create(
                            vector_store_id=vector_store.id,
                            file_id=file_obj.id
                        )
                        print(f"✅ Arquivo associado ao Vector Store: {vs_file.id}")
                    except Exception as e2:
                        print(f"❌ Falha método 2: {e2}")
                
                # Limpar
                await client.vector_stores.delete(vector_store.id)
                print("✅ Vector Store removido")
                
            except Exception as e:
                print(f"❌ Erro nos testes: {e}")

async def main():
    await explore_upload_methods()

if __name__ == "__main__":
    asyncio.run(main())