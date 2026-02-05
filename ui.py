from tkinterdnd2 import TkinterDnD, DND_FILES
import customtkinter as ctk
from pdf import save_compressed_files
from tribunais import TRIBUNAIS
import threading
from typing import Literal, Optional

class App:
    def __init__(self, master: TkinterDnD.Tk) -> None:
        self.master = master
        self.master.state("zoomed")

        self.message = ctk.StringVar(value="")
        self.tribunal = ctk.StringVar(value="Nenhum tribunal selecionado")

        self.arquivo_selecionado: Optional[str] = None

        self.index_container = ctk.CTkFrame(self.master, fg_color="transparent")
        self.loading_container = ctk.CTkFrame(self.master)

        self.index()
        self.loading()

        self.show_index()

    def hide_all(self) -> None:
        self.index_container.pack_forget()
        self.loading_container.pack_forget()

    def show_index(self) -> None:
        self.hide_all()
        self.index_container.pack(fill="both", expand=True)

    def show_loading(self) -> None:
        self.hide_all()
        self.loading_container.pack(fill="both", expand=True)

    def index(self) -> None:
        # --- ÁREA EXIBIÇÃO MENSAGEM ---

        self.show_message_frame = ctk.CTkFrame(self.index_container, height=40)
        self.show_message_frame.pack(fill="x")

        self.message_box = ctk.CTkFrame(self.show_message_frame, corner_radius=8)

        ctk.CTkLabel(
            self.message_box,
            textvariable=self.message,
            font=("Arial", 18),
        ).pack(fill="both", expand=True)

        # --- FRAME SELEÇÃO ARQUIVO

        self.file_selection_frame = ctk.CTkFrame(self.index_container)
        self.file_selection_frame.pack(fill="x", pady=30)

        self.escolha_arquivo = ctk.CTkLabel(self.file_selection_frame, text="Escolha um arquivo", font=("Arial", 20))
        self.escolha_arquivo.pack(pady=10)

        self.dnd_frame = ctk.CTkFrame(
            self.file_selection_frame,
            fg_color="transparent",
            border_width=1,
            border_color="#777777",
            corner_radius=10,
        )
        self.dnd_frame.pack(padx=30, pady=30)

        ctk.CTkLabel(
            self.dnd_frame,
            text="Arraste o arquivo aqui",
            font=("Arial", 18),
        ).pack(fill="both", expand=True, padx=20, pady=20)

        self.dnd_frame.drop_target_register(DND_FILES)
        self.dnd_frame.dnd_bind("<<Drop>>", self.on_drop)

        self.botao_muda_arq = ctk.CTkButton(
            self.file_selection_frame, font=("Arial", 18),
            text="Mudar arquivo selecionado",
            command=self.change_selected_file
        )

        # --- FRAME ESCOLHA TRIBUNAL ---

        self.tribunal_selection_frame = ctk.CTkFrame(self.index_container)
        self.tribunal_selection_frame.pack(fill="x")

        ctk.CTkLabel(self.tribunal_selection_frame, text="Escolha o tribunal", font=("Arial", 20)).pack()

        ctk.CTkLabel(
            self.tribunal_selection_frame,
            text="Tribunal selecionado:",
            font=("Arial", 18),
        ).pack(pady=(10, 0))

        ctk.CTkLabel(
            self.tribunal_selection_frame,
            textvariable=self.tribunal,
            font=("Arial", 18),
            text_color="#4da6ff",
        ).pack(pady=(0, 10))

        list_frame = ctk.CTkScrollableFrame(self.tribunal_selection_frame, width=550, height=300)
        list_frame.pack()

        for nome in TRIBUNAIS.keys():
            btn = ctk.CTkButton(
                list_frame,
                text=nome,
                anchor="w",
                command=lambda n=nome: self.tribunal.set(n),
            )
            btn.pack(fill="x", pady=2)

        ctk.CTkButton(
            self.index_container,
            text="Comprimir PDF",
            command=self.start_compression,
            font=("Arial", 18),
        ).pack(pady=50)

    def show_message(self, msg: str, type: Literal["error", "success"]) -> None:    
        color = "#8B0000" if type == "error" else "#28a745"

        self.message_box.configure(fg_color=color)
        self.message_box.pack(fill="x", padx=20, pady=5)

        self.message.set(msg)

    def hide_message(self) -> None:
        self.message_box.pack_forget()

    def on_drop(self, event) -> None:
        files = self.master.tk.splitlist(event.data)
        self.arquivo_selecionado = files[0]

        self.dnd_frame.pack_forget()
        self.escolha_arquivo.pack_forget()

        self.label_selecionado = ctk.CTkLabel(self.file_selection_frame, text=f"Arquivo selecionado:\n{self.arquivo_selecionado}", font=("Arial", 20))
        self.label_selecionado.pack(pady=10)

        self.botao_muda_arq.pack(pady=10)

    def start_compression(self) -> None:
        if not self.arquivo_selecionado:
            self.show_message("Selecione um arquivo", "error")
            return

        if not self.tribunal.get() or self.tribunal.get() == "Nenhum tribunal selecionado":
            self.show_message("Selecione um tribunal", "error")
            return

        self.show_loading()

        thread = threading.Thread(
            target=self.run_compression,
            daemon=True,
        )
        thread.start()

    def run_compression(self) -> None:
        try:
            output_path = save_compressed_files(
                self.arquivo_selecionado,
                TRIBUNAIS[self.tribunal.get()].max_pdf_mb,
            )
            self.show_message(f"Arquivo salvo em {output_path}", "success")
        except Exception as e:
            self.show_message(str(e), "error")

        self.change_selected_file()
        self.show_index()

    def change_selected_file(self) -> None:
        self.label_selecionado.pack_forget()
        self.botao_muda_arq.pack_forget()

        self.escolha_arquivo.pack(pady=10)
        self.dnd_frame.pack(padx=30, pady=30)

    def loading(self) -> None:
        box = ctk.CTkFrame(self.loading_container, corner_radius=12)
        box.pack(expand=True)

        ctk.CTkLabel(
            box,
            text="Comprimindo PDF...",
            font=("Arial", 18),
        ).pack(padx=20, pady=(20, 10))

        progress = ctk.CTkProgressBar(box, mode="indeterminate", width=250)
        progress.pack(padx=20, pady=(0, 20))
        progress.start()
