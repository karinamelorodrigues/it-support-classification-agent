# agent_ai_foundry_vector_fixed.py
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
        self.root.title("Agent Suporte TI - Vector Store Real")
        self.root.geometry("800x600")
        
        self.is_connected = False
        self.agents_client = None
        self.agent = None
        self.thread = None
        self.vector_store = None
        self.uploaded_files = []
        self.credential = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Frame principal
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Controles
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        self.btn = tk.Button(control_frame, text="🔄 Conectar com Vector Store", 
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
        self.add_message("system", "🚀 Agent com Vector Store Real no Azure AI Foundry")
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
    
    async def create_vector_store_with_files(self, knowledge_base_path: str):
        """Cria um Vector Store e adiciona arquivos da base de conhecimento"""
        
        print("📚 Criando Vector Store para base de conhecimento...")
        
        # Criar Vector Store
        vector_store = await self.agents_client.vector_stores.create(
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
                # Fazer upload dos arquivos para o Vector Store
                batch = await self.agents_client.vector_stores.upload_files(
                    vector_store_id=vector_store.id,
                    files=files_to_upload
                )
                print(f"✅ {len(files_to_upload)} arquivos enviados para o Vector Store")
                self.uploaded_files = files_to_upload
                return vector_store
            else:
                print("⚠️  Nenhum arquivo encontrado na pasta knowledge_base")
                return None
        else:
            print("❌ Pasta knowledge_base não encontrada")
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
        try:
            # Executar a conexão assíncrona em um novo event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._connect_async())
            loop.close()
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Erro na conexão: {error_msg}")
            self.root.after(0, lambda: self.add_message("error", f"Conexão: {error_msg}"))
            self.root.after(0, self._update_disconnected_ui)
    
    async def _connect_async(self):
        """Conexão assíncrona com Azure AI"""
        from azure.ai.agents.aio import AgentsClient
        from azure.identity.aio import DefaultAzureCredential
        
        endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
        model_name = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")
        
        if not endpoint or not model_name:
            self.root.after(0, lambda: self.add_message("error", "Variáveis de ambiente não configuradas"))
            self.root.after(0, self._update_disconnected_ui)
            return
        
        try:
            # Criar clients assíncronos
            self.credential = DefaultAzureCredential()
            self.agents_client = AgentsClient(
                endpoint=endpoint, 
                credential=self.credential
            )
            
            # Ler instruções
            instructions = self.read_instructions()
            
            # 1. Criar Vector Store com arquivos
            self.vector_store = await self.create_vector_store_with_files("./knowledge_base")
            
            if not self.vector_store:
                self.root.after(0, lambda: self.add_message("error", "Falha ao criar Vector Store"))
                self.root.after(0, self._update_disconnected_ui)
                return
            
            # 2. Criar o agent com Vector Store
            tools = []
            if self.vector_store:
                tools = [{
                    "type": "file_search",
                    "vector_store_ids": [self.vector_store.id]
                }]
            
            self.agent = await self.agents_client.create_agent(
                model=model_name,
                instructions=instructions,
                tools=tools,
                name=f"suporte-ti-agent-{int(time.time())}"
            )
            
            print(f"✅ Agente criado com Vector Store: {self.agent.id}")
            
            # 3. Criar thread
            self.thread = await self.agents_client.create_thread()
            
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
        self.btn.config(state=tk.DISABLED, text="Desconectando...")
        threading.Thread(target=self._disconnect_thread, daemon=True).start()
    
    def _disconnect_thread(self):
        try:
            # Executar desconexão assíncrona
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._disconnect_async())
            loop.close()
            
        except Exception as e:
            print(f"Erro na desconexão: {e}")
        finally:
            self.is_connected = False
            self.root.after(0, self._update_disconnected_ui)
    
    async def _disconnect_async(self):
        """Desconexão assíncrona"""
        try:
            if self.agent and hasattr(self.agent, 'id'):
                await self.agents_client.delete_agent(self.agent.id)
                self.add_message("system", "🔧 Agent removido")
            
            if self.vector_store and hasattr(self.vector_store, 'id'):
                await self.agents_client.vector_stores.delete(self.vector_store.id)
                self.add_message("system", "🗑️ Vector Store removido")
            
            if self.thread and hasattr(self.thread, 'id'):
                await self.agents_client.delete_thread(self.thread.id)
                self.add_message("system", "📝 Thread removida")
            
            # Fechar clients
            if self.agents_client:
                await self.agents_client.close()
            if self.credential:
                await self.credential.close()
                
        except Exception as e:
            print(f"Erro na desconexão assíncrona: {e}")
    
    def use_example(self, example):
        if self.is_connected:
            self.entry.delete(0, tk.END)
            self.entry.insert(0, example)
            self.send_message()
        else:
            messagebox.showwarning("Aviso", "Conecte-se primeiro ao Azure AI")
    
    def send_message(self, event=None):
        if not self.is_connected:
            return
        
        message = self.entry.get().strip()
        if message:
            self.entry.delete(0, tk.END)
            self.add_message("user", message)
            threading.Thread(target=lambda: self._process_message(message), daemon=True).start()
    
    def _process_message(self, message):
        try:
            # Executar processamento assíncrono
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self._process_message_async(message))
            loop.close()
            
            if result:
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
            await self.agents_client.create_message(
                thread_id=self.thread.id,
                content=message,
                role="user"
            )
            
            # Executar run
            run = await self.agents_client.create_run(
                thread_id=self.thread.id,
                agent_id=self.agent.id
            )
            
            # Aguardar conclusão
            while run.status in ['queued', 'in_progress']:
                await asyncio.sleep(0.5)
                run = await self.agents_client.get_run(
                    thread_id=self.thread.id,
                    run_id=run.id
                )
            
            if run.status == 'completed':
                # Buscar mensagens
                messages_page = await self.agents_client.list_messages(thread_id=self.thread.id)
                
                agent_response = ""
                for message in messages_page.data:
                    if message.role == 'assistant':
                        for content in message.content:
                            if hasattr(content, 'text') and hasattr(content.text, 'value'):
                                agent_response += content.text.value
                        
                        if agent_response:
                            break
                
                return agent_response
            else:
                return f"Erro no run: {run.status}"
                
        except Exception as e:
            return f"Erro: {str(e)}"

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