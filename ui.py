from tkinterdnd2 import TkinterDnD, DND_FILES
import customtkinter as ctk
from pdf import save_compressed_files
from tribunais import TRIBUNAIS


class App:
    def __init__(self, master: TkinterDnD.Tk) -> None:
        self.master = master
        self.master.geometry("960x540")

        self.nome_arq = None
        self.error_msg = None
        self.success_msg = None
        self.tribunal = ctk.StringVar()

        self.index()

    def index(self) -> None:
        self.hide_all()

        frame = ctk.CTkFrame(self.master)
        frame.pack(fill="both", expand=True)

        if self.error_msg:
            self.show_msg(frame, self.error_msg, "#8B0000")
        elif self.success_msg:
            self.show_msg(frame, self.success_msg, "#28a745")

        ctk.CTkLabel(frame, text="Escolha o PDF", font=("Arial", 18)).pack(
            pady=(40, 10)
        )

        file_label = self.nome_arq if self.nome_arq else "Nenhum arquivo selecionado"
        ctk.CTkButton(
            frame,
            text=file_label,
            font=("Arial", 18),
            command=self.choose_file,
        ).pack(pady=(0, 20))

        ctk.CTkLabel(frame, text="Escolha o tribunal", font=("Arial", 16)).pack(
            pady=(0, 8)
        )

        # Lista rolável de tribunais
        list_frame = ctk.CTkScrollableFrame(frame, width=350, height=200)
        list_frame.pack()

        for nome in TRIBUNAIS.keys():
            btn = ctk.CTkButton(
                list_frame,
                text=nome,
                anchor="w",
                command=lambda n=nome: self.select_tribunal(n),
            )
            btn.pack(fill="x", pady=2)

        ctk.CTkButton(
            frame,
            text="Comprimir PDF",
            command=self.comprimir,
            font=("Arial", 14),
        ).pack(pady=(20, 0))

    def select_tribunal(self, nome: str) -> None:
        self.tribunal.set(nome)
        self.success_msg = f"Tribunal selecionado: {nome}"
        self.error_msg = None
        self.index()

    def choose_file(self) -> None:
        self.hide_all()

        frame = ctk.CTkFrame(self.master)
        frame.pack(fill="both", expand=True)

        dnd_frame = ctk.CTkFrame(
            frame,
            fg_color="transparent",
            border_width=1,
            border_color="#777777",
            corner_radius=10,
        )
        dnd_frame.pack(fill="both", expand=True, padx=30, pady=30)

        ctk.CTkLabel(
            dnd_frame,
            text="Arraste o arquivo aqui",
            font=("Arial", 18),
        ).pack(fill="both", expand=True, padx=20, pady=20)

        dnd_frame.drop_target_register(DND_FILES)
        dnd_frame.dnd_bind("<<Drop>>", self.on_drop)

    def on_drop(self, event) -> None:
        files = self.master.tk.splitlist(event.data)
        self.nome_arq = files[0]

        self.index()

    def comprimir(self) -> None:
        if not self.nome_arq:
            self.error_msg = "Selecione um arquivo"
            self.success_msg = None
            self.index()
            return

        if not self.tribunal.get():
            self.error_msg = "Selecione um tribunal"
            self.success_msg = None
            self.index()
            return

        try:
            output_path = save_compressed_files(
                self.nome_arq,
                TRIBUNAIS[self.tribunal.get()].max_pdf_mb,
            )
            self.success_msg = f"Arquivo salvo em {output_path}"
            self.error_msg = None
        except Exception as e:
            self.error_msg = str(e)
            self.success_msg = None

        self.index()

    def show_msg(self, master: ctk.CTkFrame, msg: str, color: str) -> None:
        box = ctk.CTkFrame(master, fg_color=color, corner_radius=8)
        box.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(
            box,
            text=msg,
            font=("Arial", 18),
        ).pack(fill="both", expand=True)

    def hide_all(self) -> None:
        for widget in self.master.winfo_children():
            widget.destroy()
