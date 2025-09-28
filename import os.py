import sqlite3
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess

# Cria ou conecta no banco
conn = sqlite3.connect("videos.db")
cursor = conn.cursor()

# Cria a tabela se não existir
cursor.execute("""
CREATE TABLE IF NOT EXISTS videos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    caminho TEXT
)
""")
conn.commit()

# Função para fazer upload de vídeo
def upload_video():
    caminho = filedialog.askopenfilename(
        title="Selecione o vídeo",
        filetypes=[("Arquivos de vídeo", "*.mp4 *.avi *.mov *.mkv")]
    )
    if caminho:
        nome = os.path.basename(caminho)
        cursor.execute("INSERT INTO videos (nome, caminho) VALUES (?, ?)", (nome, caminho))
        conn.commit()
        messagebox.showinfo("Sucesso", f"Vídeo '{nome}' salvo no banco!")
        listar_videos()

# Função para listar vídeos
def listar_videos():
    listbox.delete(0, tk.END)
    cursor.execute("SELECT id, nome FROM videos")
    for video in cursor.fetchall():
        listbox.insert(tk.END, f"{video[0]} - {video[1]}")

# Função para abrir vídeo
def abrir_video():
    selecionado = listbox.get(tk.ACTIVE)
    if not selecionado:
        messagebox.showwarning("Aviso", "Selecione um vídeo na lista.")
        return
    
    video_id = selecionado.split(" - ")[0]
    cursor.execute("SELECT caminho FROM videos WHERE id=?", (video_id,))
    resultado = cursor.fetchone()
    
    if resultado:
        caminho = resultado[0]
        try:
            if os.name == "nt":  # Windows
                os.startfile(caminho)
            elif os.name == "posix":  # Linux/Mac
                subprocess.call(["xdg-open", caminho])
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o vídeo: {e}")

# Interface gráfica
root = tk.Tk()
root.title("Gerenciador de Vídeos")
root.geometry("400x300")

btn_upload = tk.Button(root, text="Upload de Vídeo", command=upload_video)
btn_upload.pack(pady=10)

listbox = tk.Listbox(root, width=50)
listbox.pack(pady=10)

btn_abrir = tk.Button(root, text="Abrir Vídeo Selecionado", command=abrir_video)
btn_abrir.pack(pady=10)

listar_videos()
root.mainloop()
