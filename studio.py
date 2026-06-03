import os
import queue
import re
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from PIL import Image, ImageSequence, ImageTk

from spriteforge import SpriteForge


PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
HISTORY_LIMIT = 20

EXAMPLE_PROMPTS = [
    "sapo ninja com espada de fogo, 6 frames, 32x32",
    "capivara de armadura andando, 8 frames, 32x32",
    "monstro de pedra com olhos vermelhos, 6 frames, 32x32",
    "portal dimensional roxo girando, 8 frames, 64x64",
    "floresta escura para jogo plataforma, 1 frame, 96x48",
    "robo correndo, 8 frames, 32x32, azul neon",
    "slime verde pulando, 6 frames, 32x32",
    "explosao de fogo, 8 frames, 48x48",
]

VARIATION_SUFFIXES = [
    "variacao 2",
    "mais detalhado",
    "estilo alternativo",
]


def open_path(path):
    path = Path(path)
    if not path.exists():
        messagebox.showwarning("Arquivo nao encontrado", f"Nao encontrei:\n{path}")
        return

    if sys.platform.startswith("win"):
        os.startfile(str(path))  # noqa: S606 - local desktop helper.
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path)])


class SpriteForgeStudio(tk.Tk):
    def __init__(self):
        super().__init__()
        os.chdir(PROJECT_ROOT)

        self.title("SpriteForge Studio")
        self.geometry("1040x720")
        self.minsize(880, 620)

        self.forge = SpriteForge()
        self.last_result = None
        self.last_prompt = ""
        self.history = []
        self.active_job_id = 0
        self.is_generating = False
        self.result_queue = queue.Queue()
        self.poll_job = None
        self.variation_index = 0

        self.preview_frames = []
        self.preview_index = 0
        self.preview_job = None

        self.prompt_text = None
        self.examples_list = None
        self.history_list = None
        self.preview_label = None
        self.generate_button = None
        self.variation_button = None
        self.upscale_button = None
        self.pack_button = None

        self.status_var = tk.StringVar(value="Pronto para gerar.")
        self.asset_var = tk.StringVar(value="Asset: -")
        self.generator_var = tk.StringVar(value="Generator: -")
        self.fallback_var = tk.StringVar(value="Fallback: -")
        self.preview_path_var = tk.StringVar(value="Preview GIF: -")
        self.output_path_var = tk.StringVar(value="Output: -")
        self.metadata_path_var = tk.StringVar(value="Metadata: -")

        self._build_ui()
        self._set_prompt(EXAMPLE_PROMPTS[0])

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        root = ttk.Frame(self, padding=14)
        root.grid(row=0, column=0, sticky="nsew")
        root.columnconfigure(0, weight=3)
        root.columnconfigure(1, weight=2)
        root.rowconfigure(2, weight=1)

        title = ttk.Label(root, text="SpriteForge Studio", font=("Segoe UI", 18, "bold"))
        title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        prompt_frame = ttk.LabelFrame(root, text="Prompt")
        prompt_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        prompt_frame.columnconfigure(0, weight=1)

        self.prompt_text = tk.Text(prompt_frame, height=4, wrap="word", undo=True)
        self.prompt_text.grid(row=0, column=0, sticky="ew", padx=8, pady=8)

        button_row = ttk.Frame(prompt_frame)
        button_row.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 8))

        self.generate_button = ttk.Button(button_row, text="Gerar Asset", command=self._generate_asset)
        self.generate_button.pack(side="left")

        self.variation_button = ttk.Button(button_row, text="Gerar variação", command=self._generate_variation)
        self.variation_button.pack(side="left", padx=(8, 0))

        self.upscale_button = ttk.Button(button_row, text="Aumentar para 64x64", command=self._generate_64x64)
        self.upscale_button.pack(side="left", padx=(8, 0))

        self.pack_button = ttk.Button(button_row, text="Gerar pack", command=self._generate_pack)
        self.pack_button.pack(side="left", padx=(8, 0))

        ttk.Button(button_row, text="Abrir pasta de outputs", command=self._open_outputs).pack(
            side="left", padx=(8, 0)
        )
        ttk.Button(button_row, text="Abrir ultimo asset", command=self._open_last_asset).pack(
            side="left", padx=(8, 0)
        )
        ttk.Button(button_row, text="Abrir GIF", command=self._open_last_gif).pack(
            side="left", padx=(8, 0)
        )

        side_frame = ttk.Frame(root)
        side_frame.grid(row=1, column=1, rowspan=2, sticky="nsew")
        side_frame.columnconfigure(0, weight=1)
        side_frame.rowconfigure(0, weight=1)
        side_frame.rowconfigure(1, weight=1)

        examples_frame = ttk.LabelFrame(side_frame, text="Exemplos prontos")
        examples_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        examples_frame.columnconfigure(0, weight=1)
        examples_frame.rowconfigure(0, weight=1)

        self.examples_list = tk.Listbox(examples_frame, height=10, activestyle="dotbox", exportselection=False)
        self.examples_list.grid(row=0, column=0, sticky="nsew", padx=(8, 0), pady=8)
        examples_scroll = ttk.Scrollbar(examples_frame, orient="vertical", command=self.examples_list.yview)
        examples_scroll.grid(row=0, column=1, sticky="ns", pady=8, padx=(0, 8))
        self.examples_list.configure(yscrollcommand=examples_scroll.set)

        for prompt in EXAMPLE_PROMPTS:
            self.examples_list.insert(tk.END, prompt)
        self.examples_list.bind("<<ListboxSelect>>", self._example_selected)

        history_frame = ttk.LabelFrame(side_frame, text="Historico da sessao")
        history_frame.grid(row=1, column=0, sticky="nsew")
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)

        self.history_list = tk.Listbox(history_frame, height=10, activestyle="dotbox", exportselection=False)
        self.history_list.grid(row=0, column=0, sticky="nsew", padx=(8, 0), pady=8)
        history_scroll = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_list.yview)
        history_scroll.grid(row=0, column=1, sticky="ns", pady=8, padx=(0, 8))
        self.history_list.configure(yscrollcommand=history_scroll.set)
        self.history_list.bind("<<ListboxSelect>>", self._history_selected)

        result_frame = ttk.LabelFrame(root, text="Resultado")
        result_frame.grid(row=2, column=0, sticky="nsew", padx=(0, 10), pady=(12, 0))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(7, weight=1)

        ttk.Label(result_frame, textvariable=self.status_var).grid(row=0, column=0, sticky="w", padx=8, pady=(8, 2))
        ttk.Label(result_frame, textvariable=self.asset_var).grid(row=1, column=0, sticky="w", padx=8, pady=2)
        ttk.Label(result_frame, textvariable=self.generator_var).grid(row=2, column=0, sticky="w", padx=8, pady=2)
        ttk.Label(result_frame, textvariable=self.fallback_var).grid(row=3, column=0, sticky="w", padx=8, pady=2)
        ttk.Label(result_frame, textvariable=self.preview_path_var, wraplength=600).grid(
            row=4, column=0, sticky="w", padx=8, pady=2
        )
        ttk.Label(result_frame, textvariable=self.output_path_var, wraplength=600).grid(
            row=5, column=0, sticky="w", padx=8, pady=2
        )
        ttk.Label(result_frame, textvariable=self.metadata_path_var, wraplength=600).grid(
            row=6, column=0, sticky="w", padx=8, pady=(2, 8)
        )

        self.preview_label = ttk.Label(
            result_frame,
            text="A preview do ultimo asset aparece aqui depois da geracao.",
            anchor="center",
            relief="solid",
            padding=10,
        )
        self.preview_label.grid(row=7, column=0, sticky="nsew", padx=8, pady=(0, 8))

    def _read_prompt(self):
        return self.prompt_text.get("1.0", "end-1c").strip()

    def _set_prompt(self, prompt):
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert("1.0", prompt)
        self.prompt_text.mark_set(tk.INSERT, tk.END)
        self.prompt_text.focus_set()

    def _example_selected(self, _event):
        selection = self.examples_list.curselection()
        if not selection:
            return

        prompt = self.examples_list.get(selection[0])
        self._set_prompt(prompt)
        self.status_var.set("Exemplo carregado no prompt.")

    def _history_selected(self, _event):
        selection = self.history_list.curselection()
        if not selection:
            return

        entry = self.history[selection[0]]
        self._set_prompt(entry["prompt"])
        self.last_prompt = entry["prompt"]
        self.last_result = entry["result"]
        self._show_result(entry["result"], status="Historico selecionado.")
        self._load_preview(entry["result"]["preview_gif"])

    def _generate_asset(self):
        self._start_generation(self._read_prompt())

    def _generate_variation(self):
        prompt = self._read_prompt()
        if not prompt:
            messagebox.showwarning("Prompt vazio", "Digite um prompt antes de gerar uma variacao.")
            return

        self.variation_index += 1
        self._start_generation(prompt, variant_id=self.variation_index)

    def _generate_pack(self):
        prompt = self._read_prompt()
        if not prompt:
            messagebox.showwarning("Prompt vazio", "Digite um prompt antes de gerar um pack.")
            return

        pack_prompt = prompt if prompt.lower().strip().startswith("pack ") else f"pack {prompt}"
        self._start_generation(pack_prompt, is_pack=True)

    def _generate_64x64(self):
        prompt = self._read_prompt()
        if not prompt:
            messagebox.showwarning("Prompt vazio", "Digite um prompt antes de aumentar.")
            return

        resized_prompt = self._prompt_64x64(prompt)
        self._set_prompt(resized_prompt)
        self._start_generation(resized_prompt)

    def _prompt_64x64(self, prompt):
        if re.search(r"32\s*x\s*32", prompt, flags=re.IGNORECASE):
            return re.sub(r"32\s*x\s*32", "64x64", prompt, count=1, flags=re.IGNORECASE)
        if re.search(r"\d+\s*x\s*\d+", prompt):
            return re.sub(r"\d+\s*x\s*\d+", "64x64", prompt, count=1)
        return f"{prompt}, 64x64"

    def _start_generation(self, prompt, variant_id=None, is_pack=False):
        prompt = prompt.strip()
        if not prompt:
            messagebox.showwarning("Prompt vazio", "Digite um prompt antes de gerar.")
            return

        self.active_job_id += 1
        job_id = self.active_job_id
        self.last_result = None
        self.last_prompt = prompt
        self._set_busy(True)
        self._clear_result(prompt)

        worker = threading.Thread(target=self._run_generation, args=(job_id, prompt, variant_id, is_pack), daemon=True)
        worker.start()
        self._schedule_result_poll()

    def _run_generation(self, job_id, prompt, variant_id, is_pack):
        try:
            if is_pack:
                result = self.forge.generate_pack(prompt)
            else:
                result = self.forge.generate(prompt, variant_id=variant_id)
        except Exception as exc:  # noqa: BLE001 - UI boundary.
            self.result_queue.put(("error", job_id, prompt, exc))
            return

        self.result_queue.put(("ok", job_id, prompt, result))

    def _schedule_result_poll(self):
        if self.poll_job is None:
            self.poll_job = self.after(50, self._poll_results)

    def _poll_results(self):
        self.poll_job = None
        handled_active_job = False

        while True:
            try:
                status, job_id, prompt, payload = self.result_queue.get_nowait()
            except queue.Empty:
                break

            if job_id != self.active_job_id:
                continue

            handled_active_job = True
            if status == "ok":
                self._generation_finished(job_id, prompt, payload)
            else:
                self._generation_failed(job_id, payload)
            break

        if self.is_generating and not handled_active_job:
            self._schedule_result_poll()

    def _generation_finished(self, job_id, prompt, result):
        if job_id != self.active_job_id:
            return

        self.last_prompt = prompt
        self.last_result = result
        self._set_busy(False)
        self._show_result(result, status=f"Geracao concluida para: {prompt}")
        self._add_history(prompt, result)
        self._load_preview(result["preview_gif"])

    def _generation_failed(self, job_id, exc):
        if job_id != self.active_job_id:
            return

        self._set_busy(False)
        self.status_var.set("Erro ao gerar asset.")
        self.preview_label.configure(image="", text="Falha ao gerar preview.")
        messagebox.showerror("Erro na geracao", str(exc))

    def _set_busy(self, busy):
        self.is_generating = busy
        state = "disabled" if busy else "normal"
        self.generate_button.configure(state=state)
        self.variation_button.configure(state=state)
        self.upscale_button.configure(state=state)
        self.pack_button.configure(state=state)

    def _clear_result(self, prompt):
        self.status_var.set(f"Gerando asset com prompt: {prompt}")
        self.asset_var.set("Asset: gerando...")
        self.generator_var.set("Generator: -")
        self.fallback_var.set("Fallback: -")
        self.preview_path_var.set("Preview GIF: -")
        self.output_path_var.set("Output: -")
        self.metadata_path_var.set("Metadata: -")
        self._clear_preview(text="Gerando preview...")

    def _show_result(self, result, status):
        preview_path = Path(result["preview_gif"]).resolve()
        output_dir = Path(result["output_dir"]).resolve()
        metadata_path = Path(result["metadata"]).resolve()

        self.status_var.set(status)
        self.asset_var.set(f"Asset: {result['asset']}")
        self.generator_var.set(f"Generator: {result['generator']}")
        self.fallback_var.set(f"Fallback: {result['fallback']}")
        self.preview_path_var.set(f"Preview GIF: {preview_path}")
        self.output_path_var.set(f"Output: {output_dir}")
        self.metadata_path_var.set(f"Metadata: {metadata_path}")

    def _add_history(self, prompt, result):
        entry = {"prompt": prompt, "result": result}
        self.history.insert(0, entry)
        label = f"{result['asset']} | {result['generator']} | {prompt}"
        self.history_list.insert(0, label)

        while len(self.history) > HISTORY_LIMIT:
            self.history.pop()
            self.history_list.delete(tk.END)

    def _open_outputs(self):
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        open_path(OUTPUTS_DIR)

    def _open_last_asset(self):
        if not self.last_result:
            messagebox.showinfo("Nenhum asset", "Gere um asset ou selecione um item do historico primeiro.")
            return
        open_path(self.last_result["output_dir"])

    def _open_last_gif(self):
        if not self.last_result:
            messagebox.showinfo("Nenhum GIF", "Gere um asset ou selecione um item do historico primeiro.")
            return
        open_path(self.last_result["preview_gif"])

    def _clear_preview(self, text):
        if self.preview_job:
            self.after_cancel(self.preview_job)
            self.preview_job = None
        self.preview_frames = []
        self.preview_index = 0
        self.preview_label.configure(image="", text=text)
        self.preview_label.image = None

    def _load_preview(self, gif_path):
        self._clear_preview(text="Carregando preview...")
        path = Path(gif_path)
        if not path.exists():
            self.preview_label.configure(text="Preview GIF nao encontrado.")
            return

        try:
            with Image.open(path) as image:
                frames = []
                for frame in ImageSequence.Iterator(image):
                    frame = frame.convert("RGBA")
                    frame.thumbnail((360, 300), Image.Resampling.NEAREST)
                    frames.append(ImageTk.PhotoImage(frame))
        except Exception:
            self._load_first_frame(path)
            return

        if not frames:
            self._load_first_frame(path)
            return

        self.preview_frames = frames
        self.preview_index = 0
        self._animate_preview()

    def _load_first_frame(self, gif_path):
        try:
            with Image.open(gif_path) as image:
                frame = image.convert("RGBA")
                frame.thumbnail((360, 300), Image.Resampling.NEAREST)
                photo = ImageTk.PhotoImage(frame)
        except Exception:
            self.preview_label.configure(text="Preview gerado. Use o botao Abrir GIF para ver.")
            return

        self.preview_label.configure(image=photo, text="")
        self.preview_label.image = photo

    def _animate_preview(self):
        if not self.preview_frames:
            return

        frame = self.preview_frames[self.preview_index]
        self.preview_label.configure(image=frame, text="")
        self.preview_label.image = frame
        self.preview_index = (self.preview_index + 1) % len(self.preview_frames)
        self.preview_job = self.after(120, self._animate_preview)


def main():
    app = SpriteForgeStudio()
    app.mainloop()


if __name__ == "__main__":
    main()
