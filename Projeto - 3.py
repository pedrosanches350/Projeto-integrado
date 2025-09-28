import os
import shutil
import sqlite3
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import platform
import uuid

# --- setup inicial ---
os.makedirs("nuvem", exist_ok=True)   # pasta onde guardamos os vídeos "na nuvem" (simulada)
conn = sqlite3.connect("videos.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS videos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    caminho TEXT
)
""")
conn.commit()

# --- funções principais ---
def upload_video():
    origem = filedialog.askopenfilename(
        title="Selecione o vídeo para upload",
        filetypes=[("Arquivos de vídeo", "*.mp4 *.avi *.mov *.mkv")]
    )
    if not origem:
        return

    nome_original = os.path.basename(origem)
    _, ext = os.path.splitext(nome_original)
    unico = f"{uuid.uuid4().hex}{ext}"
    destino = os.path.join("nuvem", unico)

    try:
        shutil.copy2(origem, destino)  # copia o arquivo pra pasta "nuvem"
        cursor.execute("INSERT INTO videos (nome, caminho) VALUES (?, ?)", (nome_original, destino))
        conn.commit()
        messagebox.showinfo("Sucesso", f"Vídeo '{nome_original}' salvo na nuvem.")
        listar_videos()
    except Exception as e:
        messagebox.showerror("Erro ao fazer upload", f"Ocorreu um erro: {e}")

def listar_videos():
    listbox.delete(0, tk.END)
    cursor.execute("SELECT id, nome FROM videos ORDER BY id DESC")
    for vid in cursor.fetchall():
        listbox.insert(tk.END, f"{vid[0]} - {vid[1]}")

def abrir_video():
    selecionado = listbox.get(tk.ACTIVE)
    if not selecionado:
        messagebox.showwarning("Aviso", "Selecione um vídeo na lista.")
        return

    video_id = selecionado.split(" - ")[0]
    try:
        video_id = int(video_id)
    except ValueError:
        messagebox.showerror("Erro", "ID do vídeo inválido.")
        return

    cursor.execute("SELECT caminho FROM videos WHERE id = ?", (video_id,))
    row = cursor.fetchone()
    if not row:
        messagebox.showerror("Erro", "Caminho do vídeo não encontrado no banco.")
        return

    caminho = row[0]
    if not os.path.exists(caminho):
        messagebox.showerror("Erro", f"Arquivo não encontrado:\n{caminho}")
        return

    sistema = platform.system()
    try:
        if sistema == "Windows":
            os.startfile(caminho)
        elif sistema == "Darwin":  # macOS
            subprocess.run(["open", caminho], check=False)
        else:  # Linux/others
            subprocess.run(["xdg-open", caminho], check=False)
    except Exception as e:
        messagebox.showerror("Erro ao abrir vídeo", f"Ocorreu um erro ao abrir o vídeo:\n{e}")

def apagar_video():
    selecionado = listbox.get(tk.ACTIVE)
    if not selecionado:
        messagebox.showwarning("Aviso", "Selecione um vídeo para apagar.")
        return

    video_id = selecionado.split(" - ")[0]
    try:
        video_id = int(video_id)
    except ValueError:
        messagebox.showerror("Erro", "ID do vídeo inválido.")
        return

    cursor.execute("SELECT nome, caminho FROM vídeos WHERE id = ?".replace("vídeos","videos"), (video_id,))  # correção por segurança
    row = cursor.fetchone()
    if not row:
        messagebox.showerror("Erro", "Registro do vídeo não encontrado.")
        return

    nome, caminho = row
    confirmar = messagebox.askyesno("Confirmar exclusão", f"Tem certeza que deseja apagar '{nome}'?\n(O arquivo será removido da pasta 'nuvem'.)")
    if not confirmar:
        return

    try:
        if os.path.exists(caminho):
            os.remove(caminho)  # remove o arquivo do disco
        cursor.execute("DELETE FROM videos WHERE id = ?", (video_id,))
        conn.commit()
        listar_videos()
        messagebox.showinfo("Removido", f"Vídeo '{nome}' removido com sucesso.")
    except Exception as e:
        messagebox.showerror("Erro ao apagar", f"Não foi possível apagar o vídeo:\n{e}")

def on_close():
    try:
        conn.close()
    except:
        pass
    root.destroy()

# --- interface ---
root = tk.Tk()
root.title("Gerenciador de Vídeos (Protótipo)")
root.geometry("500x350")

frame_botoes = tk.Frame(root)
frame_botoes.pack(pady=10)

btn_upload = tk.Button(frame_botoes, text="Upload de Vídeo", command=upload_video, width=18)
btn_upload.grid(row=0, column=0, padx=5)

btn_abrir = tk.Button(frame_botoes, text="Abrir Vídeo Selecionado", command=abrir_video, width=18)
btn_abrir.grid(row=0, column=1, padx=5)

btn_apagar = tk.Button(frame_botoes, text="Apagar Vídeo", command=apagar_video, width=18)
btn_apagar.grid(row=0, column=2, padx=5)

listbox = tk.Listbox(root, width=70, height=12)
listbox.pack(pady=10)

# duplo clique para abrir também
listbox.bind("<Double-1>", lambda e: abrir_video())

listar_videos()
root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
