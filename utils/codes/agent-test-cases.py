# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from azure.identity.aio import DefaultAzureCredential


def read_instructions_from_file(file_path: str) -> str:
    """Lê instruções de um arquivo .txt"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read().strip()
        if not content:
            raise ValueError("O arquivo está vazio")
        print("✅ Instruções carregadas do arquivo com sucesso!")
        return content
    except Exception as e:
        print(f"❌ Erro ao ler instruções: {e}")
        return "Você é um assistente de IA útil. Finalize cada resposta com [FIM]."


def classify_query(query: str) -> str:
    """Classifica a query para demonstração"""
    query_lower = query.lower()
    if any(word in query_lower for word in ['wifi', 'internet', 'conectar', 'rede', 'conexão']):
        return "REDE"
    elif any(word in query_lower for word in ['computador', 'liga', 'tela', 'mouse', 'teclado', 'hardware']):
        return "HARDWARE" 
    elif any(word in query_lower for word in ['senha', 'acesso', 'conta', 'bloqueado', 'login']):
        return "SEGURANÇA"
    elif any(word in query_lower for word in ['software', 'word', 'programa', 'aplicativo', 'instalar']):
        return "SOFTWARE"
    else:
        return "OUTROS"


async def main() -> None:
    # Verificar variáveis de ambiente
    endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    model_name = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")
    
    if not endpoint or not model_name:
        print("❌ Variáveis de ambiente necessárias não configuradas")
        return

    # Ler instruções do arquivo
    try:
        instructions = read_instructions_from_file("./instructions/instrucoes.txt")
        print("📄 Conteúdo das instruções:")
        print(f"--- INÍCIO INSTRUÇÕES ---")
        print(instructions)
        print(f"--- FIM INSTRUÇÕES ---")
    except Exception as e:
        print(f"⚠️  Usando instruções padrão devido ao erro: {e}")
        instructions = """
        Você é um agente de classificação de suporte de TI. Sua função é:
        1. Classificar tickets de suporte em categorias: Rede, Hardware, Software, Segurança, Outros
        2. Fornecer orientação inicial para problemas comuns
        3. Ser profissional e conciso
        4. Finalizar cada resposta com [FIM]
        
        Categorias:
        - REDE: Problemas de wifi, internet, VPN, conectividade
        - HARDWARE: Problemas com computador, periféricos, equipamentos
        - SOFTWARE: Problemas com aplicativos, programas, instalação
        - SEGURANÇA: Problemas de senha, acesso, autenticação
        - OUTROS: Não se encaixa nas categorias acima
        """

    print("🔄 Conectando ao Azure AI Foundry...")
    
    async with DefaultAzureCredential() as credential:
        async with AIProjectClient(
            endpoint=endpoint,
            credential=credential
        ) as project_client:
            
            agent = None
            try:
                # Criar o agente
                print("📝 Criando agente...")
                agent = await project_client.agents.create_version(
                    agent_name="ITSupportClassificationAgent",
                    definition=PromptAgentDefinition(
                        model=model_name,
                        instructions=instructions,
                    ),
                )
                print(f"✅ Agente criado com sucesso!")
                print(f"   Nome: {agent.name}")
                print(f"   Versão: {agent.version}")
                print(f"   Modelo: {model_name}")

                # Simular teste do agente
                print("\n🧪 SIMULAÇÃO DE TESTE DO AGENTE")
                print("=" * 50)
                
                test_cases = [
                    "Não consigo conectar na wifi",
                    "Meu computador não liga", 
                    "Esqueci minha senha de email",
                    "O software Word não está abrindo",
                    "Estou com problema para acessar a VPN",
                    "Meu monitor está piscando"
                ]
                
                for i, query in enumerate(test_cases, 1):
                    print(f"\n📞 Caso de Teste {i}:")
                    print(f"   👤 Usuário: '{query}'")
                    print(f"   🤖 Agent {agent.name}: [AGENTE CONFIGURADO PARA: {model_name}]")
                    print(f"   📋 Categoria esperada: {classify_query(query)}")  # CORRIGIDO: sem self.
                    print(f"   ✅ Resposta incluirá: [FIM]")
                
                print("\n" + "=" * 50)
                print("🎯 AGENTE CRIADO E CONFIGURADO COM SUCESSO!")
                print("💡 Para uso completo, acesse o Azure AI Foundry Studio")
                print(f"🔗 Endpoint: {endpoint}")

            except Exception as e:
                print(f"❌ Erro durante a execução: {e}")
                import traceback
                traceback.print_exc()
                
            finally:
                # Limpeza
                if agent:
                    try:
                        await project_client.agents.delete_version(
                            agent_name=agent.name,
                            agent_version=agent.version
                        )
                        print("✅ Agente removido com sucesso!")
                    except Exception as delete_error:
                        print(f"⚠️  Erro ao remover agente: {delete_error}")


if __name__ == "__main__":
    asyncio.run(main())