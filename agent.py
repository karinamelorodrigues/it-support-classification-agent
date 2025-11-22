# agent_ai_foundry_final.py
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import os
import time
import json
import asyncio
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class AIFoundryVectorAgent:
    def __init__(self, root):
        self.root = root
        self.root.title("Agent Suporte TI")
        self.root.geometry("800x600")
        
        self.is_connected = False
        self.client = None
        self.agent = None
        self.thread = None
        self.vector_store = None
        self.uploaded_files = []
        self.credential = None
        
        # Gerenciamento de event loops
        self.main_loop = asyncio.new_event_loop()
        self.worker_loop = None
        self.worker_thread = None
        
        self.setup_ui()
        self.start_worker_loop()
        
    def start_worker_loop(self):
        """Inicia um worker thread com event loop dedicado"""
        def run_worker_loop():
            self.worker_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.worker_loop)
            self.worker_loop.run_forever()
        
        self.worker_thread = threading.Thread(target=run_worker_loop, daemon=True)
        self.worker_thread.start()
        
    def run_async_in_worker(self, coro):
        """Executa uma corrotina no worker loop de forma thread-safe"""
        future = asyncio.run_coroutine_threadsafe(coro, self.worker_loop)
        return future.result()
        
    def setup_ui(self):
        # Frame principal
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Controles
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        self.btn = tk.Button(control_frame, text="🔄 Conectar no Azure AI Foundry", 
                           command=self.toggle_connection, font=('Arial', 10))
        self.btn.pack(side=tk.LEFT)
        
        self.status = tk.Label(control_frame, text="Status: Desconectado", 
                             fg="red", font=('Arial', 10))
        self.status.pack(side=tk.LEFT, padx=20)
        
        # Info de Vector Store
        self.vector_info = tk.Label(control_frame, text="Vector: Não criado", fg="orange", font=('Arial', 9))
        self.vector_info.pack(side=tk.LEFT, padx=10)
        
        # Área de chat
        self.chat = scrolledtext.ScrolledText(main_frame, height=20, wrap=tk.WORD,
                                            font=('Arial', 10))
        self.chat.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Frame de entrada
        input_frame = tk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        self.entry = tk.Entry(input_frame, font=('Arial', 10))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind('<Return>', self.send_message)
        
        self.send_btn = tk.Button(input_frame, text="Enviar", 
                                command=self.send_message, state=tk.DISABLED)
        self.send_btn.pack(side=tk.RIGHT, padx=5)
        
        # Frame de exemplos
        examples_frame = tk.LabelFrame(main_frame, text="📋 Teste a Base de Conhecimento", 
                                     font=('Arial', 9))
        examples_frame.pack(fill=tk.X, pady=5)
        
        examples = [
            "Qual procedimento para reset de senha?",
            "Como resolver problema de WiFi?",
            "Quais são os contatos de suporte?",
            "Políticas de segurança da empresa",
            "Procedimento para configurar VPN",
            "O que fazer se o computador não liga?"
        ]
        
        for i, example in enumerate(examples):
            btn = tk.Button(examples_frame, text=example, font=('Arial', 8),
                          command=lambda ex=example: self.use_example(ex))
            btn.grid(row=i//3, column=i%3, padx=2, pady=2, sticky='ew')
        
        for i in range(3):
            examples_frame.columnconfigure(i, weight=1)
        
        # Mensagem inicial
        self.add_message("system", "🚀 Agent com Vector Store no Azure AI Foundry")
        self.add_message("system", "💡 Os arquivos serão adicionados à base de conhecimento do agent")
        self.add_message("system", "📚 O agent poderá buscar informações nos documentos")
        
    def add_message(self, msg_type, message):
        """Adiciona mensagem formatada ao chat"""
        self.chat.config(state=tk.NORMAL)
        
        if msg_type == "user":
            prefix = "👤 Você: "
        elif msg_type == "agent":
            prefix = "🤖 Agent: "
        elif msg_type == "error":
            prefix = "❌ Erro: "
        else:  # system
            prefix = "⚡ "
        
        self.chat.insert(tk.END, prefix, f"{msg_type}_prefix")
        self.chat.insert(tk.END, f"{message}\n\n")
        self.chat.see(tk.END)
        self.chat.config(state=tk.DISABLED)
        
        # Configurar tags para cores
        self.chat.tag_configure("user_prefix", foreground="blue", font=('Arial', 10, 'bold'))
        self.chat.tag_configure("agent_prefix", foreground="green", font=('Arial', 10, 'bold'))
        self.chat.tag_configure("error_prefix", foreground="red", font=('Arial', 10, 'bold'))
        self.chat.tag_configure("system_prefix", foreground="gray", font=('Arial', 10, 'bold'))
    
    def read_instructions(self):
        """Lê instruções do arquivo"""
        try:
            with open("./instructions/instrucoes.txt", 'r', encoding='utf-8') as file:
                content = file.read().strip()
            if not content:
                raise ValueError("O arquivo está vazio")
            print("✅ Instruções carregadas do arquivo com sucesso!")
            return content
        except Exception as e:
            print(f"❌ Erro ao ler instruções: {e}")
            return """
            VOCÊ É UM AGENTE DE SUPORTE TÉCNICO COM ACESSO A UMA BASE DE CONHECIMENTO

            SUAS FUNÇÕES:
            1. Usar a base de conhecimento (Vector Store) para buscar informações
            2. Classificar problemas: Rede, Hardware, Software, Segurança
            3. Fornecer soluções baseadas em documentação
            4. Ser preciso e profissional

            IMPORTANTE:
            - Você tem acesso a documentos de suporte técnico via Vector Store
            - SEMPRE busque na base de conhecimento antes de responder
            - Cite procedimentos específicos quando disponíveis
            - Forneça contatos corretos da documentação

            BASE DE CONHECIMENTO DISPONÍVEL:
            - Procedimentos de suporte técnico
            - Contatos e informações de suporte
            - Políticas da empresa

            Quando o usuário fizer uma pergunta:
            1. Busque informações relevantes no Vector Store
            2. Forneça respostas baseadas na documentação
            3. Seja específico e cite fontes quando possível
            """
    
    async def upload_files_to_vector_store(self, vector_store_id, file_paths):
        """Faz upload de arquivos para o Vector Store usando os métodos corretos"""
        try:
            uploaded_files = []
            
            for file_path in file_paths:
                print(f"⬆️  Enviando arquivo: {os.path.basename(file_path)}")
                
                # Método correto: usar files.upload primeiro
                with open(file_path, 'rb') as file:
                    file_object = await self.client.files.upload(
                        file=file,
                        purpose="assistants"
                    )
                
                print(f"✅ Arquivo enviado: {file_object.id}")
                
                # Depois associar ao Vector Store
                vector_file = await self.client.vector_store_files.create(
                    vector_store_id=vector_store_id,
                    file_id=file_object.id
                )
                
                uploaded_files.append(file_object.id)
                print(f"✅ Arquivo associado ao Vector Store: {os.path.basename(file_path)}")
            
            return uploaded_files
            
        except Exception as e:
            print(f"❌ Erro no upload de arquivos: {e}")
            return []
    
    async def create_vector_store_with_files(self, knowledge_base_path: str):
        """Cria um Vector Store e adiciona arquivos da base de conhecimento"""
        try:
            print("📚 Criando Vector Store para base de conhecimento...")
            
            # Criar Vector Store
            vector_store = await self.client.vector_stores.create(
                name="knowledge-base-support-ti"
            )
            print(f"✅ Vector Store criado: {vector_store.id}")
            
            # Adicionar arquivos ao Vector Store
            if os.path.exists(knowledge_base_path):
                files_to_upload = []
                
                for file_name in os.listdir(knowledge_base_path):
                    if file_name.endswith(('.json', '.txt', '.md', '.pdf')):
                        file_path = os.path.join(knowledge_base_path, file_name)
                        files_to_upload.append(file_path)
                        print(f"📄 Arquivo encontrado: {file_name}")
                
                if files_to_upload:
                    # Fazer upload dos arquivos
                    uploaded_file_ids = await self.upload_files_to_vector_store(
                        vector_store.id, 
                        files_to_upload
                    )
                    
                    if uploaded_file_ids:
                        print(f"✅ {len(uploaded_file_ids)} arquivos enviados para o Vector Store")
                        self.uploaded_files = files_to_upload
                        return vector_store
                    else:
                        print("⚠️  Nenhum arquivo foi enviado com sucesso")
                        return vector_store
                else:
                    print("⚠️  Nenhum arquivo encontrado na pasta knowledge_base")
                    return vector_store
            else:
                print("❌ Pasta knowledge_base não encontrada")
                return vector_store
                
        except Exception as e:
            print(f"❌ Erro ao criar Vector Store: {e}")
            return None
    
    def toggle_connection(self):
        if not self.is_connected:
            self.connect_agent()
        else:
            self.disconnect_agent()
    
    def connect_agent(self):
        self.btn.config(state=tk.DISABLED, text="Conectando...")
        threading.Thread(target=self._connect_thread, daemon=True).start()
    
    def _connect_thread(self):
        """Thread para conexão usando worker loop"""
        try:
            # Executar no worker loop
            self.run_async_in_worker(self._connect_async())
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Erro na conexão: {error_msg}")
            self.root.after(0, lambda: self.add_message("error", f"Conexão: {error_msg}"))
            self.root.after(0, self._update_disconnected_ui)
    
    async def _connect_async(self):
        """Conexão assíncrona com Azure AI Foundry"""
        try:
            from azure.ai.agents.aio import AgentsClient
            from azure.identity.aio import DefaultAzureCredential
            
            endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
            model_name = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")
            
            if not endpoint or not model_name:
                self.root.after(0, lambda: self.add_message("error", "Variáveis de ambiente não configuradas"))
                self.root.after(0, self._update_disconnected_ui)
                return
            
            print("🔗 Conectando ao Azure AI Foundry...")
            
            # Criar clients assíncronos
            self.credential = DefaultAzureCredential()
            self.client = AgentsClient(endpoint=endpoint, credential=self.credential)
            print("✅ Usando AgentsClient")
            
            # Ler instruções
            instructions = self.read_instructions()
            
            # 1. Criar Vector Store com arquivos
            self.vector_store = await self.create_vector_store_with_files("./knowledge_base")
            
            if not self.vector_store:
                self.root.after(0, lambda: self.add_message("error", "Falha ao criar Vector Store"))
                self.root.after(0, self._update_disconnected_ui)
                return
            
            # 2. Criar o agent - Vamos tentar diferentes abordagens para o file_search
            try:
                # Tentar abordagem com tools
                self.agent = await self.client.create_agent(
                    model=model_name,
                    instructions=instructions,
                    tools=[{"type": "file_search"}],
                    name=f"suporte-ti-agent-{int(time.time())}"
                )
                print("✅ Agent criado com file_search tool")
            except Exception as e:
                print(f"⚠️  Não foi possível criar agent com file_search: {e}")
                # Criar agent sem tools
                self.agent = await self.client.create_agent(
                    model=model_name,
                    instructions=instructions,
                    name=f"suporte-ti-agent-{int(time.time())}"
                )
                print("✅ Agent criado sem file_search tool")
            
            print(f"✅ Agente criado: {self.agent.id}")
            
            # 3. Criar thread
            self.thread = await self.client.threads.create()
            
            self.is_connected = True
            self.root.after(0, self._update_connected_ui)
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Erro na conexão assíncrona: {error_msg}")
            import traceback
            traceback.print_exc()
            self.root.after(0, lambda: self.add_message("error", f"Conexão: {error_msg}"))
            self.root.after(0, self._update_disconnected_ui)
    
    def _update_connected_ui(self):
        self.btn.config(text="🔌 Desconectar", state=tk.NORMAL)
        self.status.config(text="Status: Conectado", fg="green")
        file_count = len(self.uploaded_files) if self.uploaded_files else 0
        self.vector_info.config(text=f"Vector: {file_count} arquivos")
        self.send_btn.config(state=tk.NORMAL)
        self.entry.config(state=tk.NORMAL)
        self.add_message("system", "✅ Conectado com Vector Store ativo!")
        self.add_message("system", f"📚 Base de conhecimento: {file_count} arquivos")
        self.add_message("system", "🤖 Faça perguntas sobre a base de conhecimento")
    
    def _update_disconnected_ui(self):
        self.btn.config(text="🔄 Conectar com Vector Store", state=tk.NORMAL)
        self.status.config(text="Status: Desconectado", fg="red")
        self.vector_info.config(text="Vector: Não criado")
        self.send_btn.config(state=tk.DISABLED)
        self.entry.config(state=tk.DISABLED)
        self.add_message("system", "🔌 Desconectado")
    
    def disconnect_agent(self):
        if not self.is_connected:
            return
            
        self.btn.config(state=tk.DISABLED, text="Desconectando...")
        threading.Thread(target=self._disconnect_thread, daemon=True).start()
    
    def _disconnect_thread(self):
        """Thread para desconexão usando worker loop"""
        try:
            self.run_async_in_worker(self._disconnect_async())
        except Exception as e:
            print(f"Erro na desconexão: {e}")
        finally:
            self.is_connected = False
            self.root.after(0, self._update_disconnected_ui)
    
    async def _disconnect_async(self):
        """Desconexão assíncrona"""
        try:
            if hasattr(self, 'client') and self.client:
                if hasattr(self, 'agent') and self.agent and hasattr(self.agent, 'id'):
                    await self.client.delete_agent(self.agent.id)
                    self.add_message("system", "🔧 Agent removido")
                
                if hasattr(self, 'vector_store') and self.vector_store and hasattr(self.vector_store, 'id'):
                    try:
                        await self.client.vector_stores.delete(self.vector_store.id)
                        self.add_message("system", "🗑️ Vector Store removido")
                    except Exception as e:
                        print(f"Erro ao remover Vector Store: {e}")
                
                if hasattr(self, 'thread') and self.thread and hasattr(self.thread, 'id'):
                    await self.client.threads.delete(self.thread.id)
                    self.add_message("system", "📝 Thread removida")
                
                # Fechar clients
                await self.client.close()
                if hasattr(self, 'credential') and self.credential:
                    await self.credential.close()
                    
        except Exception as e:
            print(f"Erro na desconexão assíncrona: {e}")
    
    def use_example(self, example):
        if self.is_connected:
            self.entry.delete(0, tk.END)
            self.entry.insert(0, example)
            self.send_message()
        else:
            messagebox.showwarning("Aviso", "Conecte-se primeiro ao Azure AI Foundry")
    
    def send_message(self, event=None):
        if not self.is_connected:
            return
        
        message = self.entry.get().strip()
        if message:
            self.entry.delete(0, tk.END)
            self.add_message("user", message)
            threading.Thread(target=lambda: self._process_message(message), daemon=True).start()
    
    def _process_message(self, message):
        """Processa mensagem usando worker loop"""
        try:
            # Executar no worker loop de forma thread-safe
            result = self.run_async_in_worker(self._process_message_async(message))
            
            if result and result != "Erro: Sem resposta":
                self.root.after(0, lambda: self.add_message("agent", result))
            else:
                self.root.after(0, lambda: self.add_message("error", "Sem resposta do agent"))
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Erro no processamento: {error_msg}")
            self.root.after(0, lambda: self.add_message("error", f"Processamento: {error_msg}"))
    
    async def _process_message_async(self, message):
        """Processa mensagem de forma assíncrona"""
        try:
            # Adicionar mensagem à thread
            await self.client.messages.create(
                thread_id=self.thread.id,
                content=message,
                role="user"
            )
            
            # Executar run
            run = await self.client.runs.create(
                thread_id=self.thread.id,
                agent_id=self.agent.id
            )
            
            # Aguardar conclusão
            while run.status in ['queued', 'in_progress']:
                await asyncio.sleep(0.5)
                run = await self.client.runs.get(
                    thread_id=self.thread.id,
                    run_id=run.id
                )
            
            if run.status == 'completed':
                # Buscar mensagens - CORREÇÃO: abordagem simplificada para AsyncList
                agent_response = ""
                
                # Obter todas as mensagens de uma vez
                all_messages = []
                messages_pager = self.client.messages.list(thread_id=self.thread.id)
                
                # Coletar todas as mensagens
                async for msg in messages_pager:
                    all_messages.append(msg)
                
                # Procurar pela resposta do assistant
                for msg in all_messages:
                    if msg.role == 'assistant':
                        # Extrair conteúdo da mensagem
                        for content in msg.content:
                            if hasattr(content, 'text'):
                                if hasattr(content.text, 'value'):
                                    agent_response += content.text.value
                                elif hasattr(content.text, 'text'):
                                    agent_response += content.text.text
                            elif hasattr(content, 'value'):
                                agent_response += content.value
                        
                        if agent_response:
                            break
                
                return agent_response if agent_response else "Sem resposta"
            else:
                return f"Erro no run: {run.status}"
                
        except Exception as e:
            return f"Erro: {str(e)}"
    
    def __del__(self):
        """Cleanup ao destruir o objeto"""
        if hasattr(self, 'worker_loop') and self.worker_loop:
            self.worker_loop.call_soon_threadsafe(self.worker_loop.stop)

def main():
    root = tk.Tk()
    app = AIFoundryVectorAgent(root)
    
    def on_closing():
        if app.is_connected:
            app.disconnect_agent()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()