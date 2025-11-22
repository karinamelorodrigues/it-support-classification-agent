import asyncio
import os
from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient

load_dotenv()

async def test_ai_foundry_connection():
    """Testar conexão básica com Azure AI Foundry"""
    
    endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    if not endpoint:
        print("❌ AZURE_AI_PROJECT_ENDPOINT não encontrado")
        return
    
    print(f"🔗 Conectando a: {endpoint}")
    
    try:
        async with DefaultAzureCredential() as credential:
            async with AIProjectClient(
                endpoint=endpoint,
                credential=credential
            ) as client:
                
                print("✅ Autenticação bem-sucedida!")
                
                # Tentar listar agents para testar a conexão
                print("📋 Listando agents...")
                agents = client.agents.list_versions(agent_name="*")
                
                agent_count = 0
                async for agent in agents:
                    print(f"   - {agent.name} (v{agent.version})")
                    agent_count += 1
                
                if agent_count == 0:
                    print("ℹ️  Nenhum agent encontrado - isso é normal para um novo projeto")
                
                print("🎉 Conexão com Azure AI Foundry funcionando!")
                
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        print("\n💡 Dicas de solução:")
        print("1. Execute 'az login' para autenticar")
        print("2. Verifique se o endpoint está correto")
        print("3. Confirme suas permissões no Azure")
        print("4. Verifique se o serviço está ativo no portal")


if __name__ == "__main__":
    asyncio.run(test_ai_foundry_connection())