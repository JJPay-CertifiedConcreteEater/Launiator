import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import webcolors
import os
import threading
import platform

class LauniatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Launiator")
        self.root.geometry("900x700")
        self.root.configure(bg="#000000")
        
        self.main_container = tk.Frame(self.root, bg="#000000")
        self.main_container.pack(fill="both", expand=True)

        self.start_splash_screen()

    def clear_screen(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def play_theme(self):
        def run_audio():
            import sys
            if platform.system() != "Windows":
                return

            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.abspath(".")

            sound_file = os.path.join(base_path, "theme.wav")
            if not os.path.exists(sound_file):
                return

            try:
                import winsound
                winsound.PlaySound(sound_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
            except:
                pass
        
        threading.Thread(target=run_audio, daemon=True).start()

    def start_splash_screen(self):
        self.clear_screen()
        self.splash_label = tk.Label(self.main_container, text="LAUNIATOR", font=("Helvetica", 42, "bold"), bg="#000000", fg="#000000")
        self.splash_label.place(relx=0.5, rely=0.5, anchor="center")
        
        self.play_theme()
        self.fade_step = 0
        self.fade_text_in()

    def fade_text_in(self):
        if self.fade_step <= 100:
            r = int(0 + (26 * self.fade_step / 100))
            g = int(0 + (115 * self.fade_step / 100))
            b = int(0 + (232 * self.fade_step / 100))
            self.splash_label.config(fg=f'#{r:02x}{g:02x}{b:02x}')
            self.fade_step += 2
            self.root.after(30, self.fade_text_in)
        else:
            self.root.after(3000, self.show_home_menu)

    def show_home_menu(self):
        self.root.configure(bg="#ffffff")
        self.main_container.configure(bg="#ffffff")
        self.clear_screen()
        self.loading_active = False

        home_frame = tk.Frame(self.main_container, bg="#ffffff")
        home_frame.place(relx=0.5, rely=0.4, anchor="center")

        tk.Label(home_frame, text="LAUNIATOR", font=("Helvetica", 42, "bold"), bg="#ffffff", fg="#1a73e8").pack()
        tk.Label(home_frame, text="IMAGE COLOR ANALYZER BY JJPAY", font=("Arial", 10, "bold"), bg="#ffffff", fg="#999999", pady=10).pack()
        
        tk.Button(home_frame, text="SCAN NEW IMAGE", command=self.process_upload, bg="#1a73e8", fg="white", font=("Arial", 12, "bold"), padx=40, pady=15, relief="flat", cursor="hand2").pack(pady=20)
        
        self.status_label = tk.Label(home_frame, text="", font=("Arial", 10), bg="#ffffff", fg="#1a73e8")
        self.progress = ttk.Progressbar(home_frame, orient="horizontal", length=200, mode="determinate")

    def show_results_page(self, colors, original_img):
        self.clear_screen()
        self.current_colors_list = []

        nav_bar = tk.Frame(self.main_container, bg="#f8f9fa", height=60)
        nav_bar.pack(fill="x")
        tk.Button(nav_bar, text="← BACK", command=self.show_home_menu, bg="#f8f9fa", fg="#1a73e8", relief="flat", font=("Arial", 10, "bold")).pack(side="left", padx=10)
        
        content_area = tk.Frame(self.main_container, bg="#ffffff")
        content_area.pack(fill="both", expand=True, padx=20, pady=20)

        left_side = tk.Frame(content_area, bg="#ffffff")
        left_side.pack(side="left", fill="both", expand=True)

        canvas = tk.Canvas(left_side, bg="#ffffff", highlightthickness=0)
        scrollbar = ttk.Scrollbar(left_side, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg="#ffffff")
        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=400)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        right_side = tk.Frame(content_area, bg="#ffffff", width=400)
        right_side.pack(side="right", fill="both", padx=(20, 0))

        img_preview = original_img.copy()
        img_preview.thumbnail((380, 380))
        self.tk_preview = ImageTk.PhotoImage(img_preview)
        tk.Label(right_side, image=self.tk_preview, bg="#ffffff").pack(pady=10)

        tk.Button(right_side, text="EXPORT TO .TXT", command=self.export_to_txt, bg="#34a853", fg="white", font=("Arial", 12, "bold"), padx=30, pady=12, relief="flat").pack(pady=20)

        for i, (count, col) in enumerate(colors, 1):
            r, g, b = col
            hex_code = '#%02x%02x%02x' % (r, g, b)
            name = self.get_color_name((r, g, b))
            self.current_colors_list.append(f"Color {i}: {name.title()}, {hex_code.upper()}")

            row = tk.Frame(self.scrollable_frame, bg="#ffffff", pady=8)
            row.pack(fill='x')
            circ = tk.Canvas(row, width=40, height=40, bg="#ffffff", highlightthickness=0)
            circ.pack(side='left', padx=10)
            circ.create_oval(2, 2, 38, 38, fill=hex_code, outline="#cccccc")
            tk.Label(row, text=f"{name.title()} ({hex_code.upper()})", bg="#ffffff", font=("Arial", 10)).pack(side='left')

    def export_to_txt(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "w") as f:
                f.write("\n".join(self.current_colors_list))
            messagebox.showinfo("Success", "Color data exported!")

    def get_color_name(self, rgb):
        try: return webcolors.rgb_to_name(rgb)
        except:
            min_colours = {}
            for name in webcolors.names("css3"):
                r_c, g_c, b_c = webcolors.name_to_rgb(name)
                dist = (r_c - rgb[0])**2 + (g_c - rgb[1])**2 + (b_c - rgb[2])**2
                min_colours[dist] = name
            return min_colours[min(min_colours.keys())]

    def process_upload(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.status_label.pack(); self.progress.pack(pady=10)
            self.loading_active = True
            img = Image.open(file_path).convert('RGB')
            processed = img.quantize(colors=100).convert('RGB')
            colors = sorted(processed.getcolors(maxcolors=100), key=lambda x: x[0], reverse=True)
            self.show_results_page(colors, img)

if __name__ == "__main__":
    root = tk.Tk()
    app = LauniatorApp(root)
    root.mainloop()
