import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Ensure current directory is on path so we can import cs2
sys.path.insert(0, os.path.dirname(__file__))
try:
    from cs2 import batch_process
except Exception:
    # fallback if module named cs2.py is not available as a module
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location('cs2', os.path.join(os.path.dirname(__file__), 'cs2.py'))
        cs2 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cs2)
        batch_process = cs2.batch_process
    except Exception as e:
        batch_process = None

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False
else:
    # also import ImageDraw when PIL present
    try:
        from PIL import ImageDraw
    except Exception:
        ImageDraw = None


class PlateGridApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('车牌识别可视化')
        self.geometry('1000x700')

        self.folder_var = tk.StringVar()

        ctrl = ttk.Frame(self)
        ctrl.pack(fill='x', padx=8, pady=6)

        ttk.Label(ctrl, text='图片文件夹：').pack(side='left')
        ttk.Entry(ctrl, textvariable=self.folder_var, width=60).pack(side='left', padx=6)
        ttk.Button(ctrl, text='浏览', command=self.browse).pack(side='left')
        ttk.Button(ctrl, text='加载并识别', command=self.load_and_run).pack(side='left', padx=6)

        # status
        self.status_var = tk.StringVar(value='准备')
        ttk.Label(self, textvariable=self.status_var).pack(fill='x', padx=8, pady=4)

        # canvas + scrollable frame
        container = ttk.Frame(self)
        container.pack(fill='both', expand=True)
        self.canvas = tk.Canvas(container)
        self.scrollbar = ttk.Scrollbar(container, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)

        self.inner_frame = ttk.Frame(self.canvas)
        # store window id so we can adjust width on resize
        self.inner_id = self.canvas.create_window((0, 0), window=self.inner_frame, anchor='nw')
        # make canvas scrollregion update when inner_frame changes
        self.inner_frame.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        # make inner frame width follow canvas width (auto-resize)
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        # enable mouse wheel scrolling (Windows)
        self.canvas.bind_all('<MouseWheel>', self._on_mousewheel)
        # also support Linux/Mac wheel buttons
        self.canvas.bind_all('<Button-4>', self._on_mousewheel)
        self.canvas.bind_all('<Button-5>', self._on_mousewheel)

        self.thumb_images = []  # keep references to PhotoImage

    def browse(self):
        path = filedialog.askdirectory()
        if path:
            self.folder_var.set(path)

    def load_and_run(self):
        folder = self.folder_var.get().strip()
        if not folder or not os.path.isdir(folder):
            messagebox.showwarning('错误', '请选择有效的图片文件夹')
            return
        if batch_process is None:
            messagebox.showerror('错误', '无法导入 cs2.batch_process，请确认 cs2.py 在同一目录且无错误')
            return

        self.status_var.set('正在识别（后台）...')
        thread = threading.Thread(target=self._run_batch, args=(folder,), daemon=True)
        thread.start()

    def _run_batch(self, folder):
        try:
            results = batch_process(folder)
        except Exception as e:
            self.status_var.set(f'识别出错: {e}')
            return
        # UI update must run in main thread
        self.after(0, lambda: self.populate_grid(folder, results))

    def populate_grid(self, folder, results):
        # clear previous
        for child in self.inner_frame.winfo_children():
            child.destroy()
        self.thumb_images.clear()

        cols = 3
        thumb_w = 320
        thumb_h = 120

        for idx, res in enumerate(results):
            r = ttk.Frame(self.inner_frame, borderwidth=1, relief='solid', padding=6)
            r.grid(row=idx // cols, column=idx % cols, padx=6, pady=6, sticky='n')

            img_name = res.get('图片名称')
            img_path = os.path.join(folder, img_name)
            status = res.get('状态') or ''

            if PIL_AVAILABLE and os.path.exists(img_path):
                try:
                    img_full = Image.open(img_path).convert('RGB')
                    # create display thumbnail with bbox overlay
                    display_img = img_full.copy()
                    display_img.thumbnail((thumb_w, thumb_h))
                    draw = None
                    if 'ImageDraw' in globals() and ImageDraw is not None:
                        draw = ImageDraw.Draw(display_img)

                    # get bbox from result if present
                    bbox = res.get('bbox')
                    if bbox and len(bbox) == 4:
                        try:
                            x1, y1, x2, y2 = map(int, bbox)
                            orig_w, orig_h = img_full.size
                            disp_w, disp_h = display_img.size
                            # scale factors (thumbnail keeps aspect, use width factor)
                            sx = disp_w / float(orig_w) if orig_w else 1.0
                            sy = disp_h / float(orig_h) if orig_h else sx
                            rx1, ry1 = int(x1 * sx), int(y1 * sy)
                            rx2, ry2 = int(x2 * sx), int(y2 * sy)
                            if draw:
                                draw.rectangle([rx1, ry1, rx2, ry2], outline='red', width=3)
                        except Exception:
                            pass

                    tkimg = ImageTk.PhotoImage(display_img)
                    img_frame = ttk.Frame(r)
                    img_frame.pack()
                    lbl = ttk.Label(img_frame, image=tkimg)
                    lbl.image = tkimg
                    lbl.pack(side='left')
                    self.thumb_images.append(tkimg)

                    # show cropped plate if bbox exists (use original crop size as requested)
                    if bbox and len(bbox) == 4:
                        try:
                            cx1, cy1, cx2, cy2 = map(int, bbox)
                            # ensure bbox within image bounds
                            ow, oh = img_full.size
                            cx1 = max(0, min(cx1, ow))
                            cy1 = max(0, min(cy1, oh))
                            cx2 = max(0, min(cx2, ow))
                            cy2 = max(0, min(cy2, oh))
                            if cx2 > cx1 and cy2 > cy1:
                                crop = img_full.crop((cx1, cy1, cx2, cy2))
                                # show crop at original crop size (no thumbnail)
                                tkcrop = ImageTk.PhotoImage(crop)
                                lbl2 = ttk.Label(img_frame, image=tkcrop)
                                lbl2.image = tkcrop
                                lbl2.pack(side='left', padx=6)
                                self.thumb_images.append(tkcrop)
                        except Exception:
                            pass
                except Exception:
                    ttk.Label(r, text='无法加载图片').pack()
            else:
                ttk.Label(r, text=img_name).pack()

            # labels
            plate = res.get('识别结果', '')
            color = res.get('车牌颜色', '')
            ptype = res.get('车牌类型', '')
            location = res.get('所属地区', '')

            info = f"{plate}\n{color} | {ptype}\n{location}\n{status}"
            ttk.Label(r, text=info, justify='center').pack(pady=4)

        self.status_var.set(f'加载完成：{len(results)} 张（显示已更新）')

    def _on_canvas_configure(self, event):
        # make the inner frame the same width as the canvas for auto-resize
        try:
            canvas_width = event.width
            self.canvas.itemconfig(self.inner_id, width=canvas_width)
        except Exception:
            pass

    def _on_mousewheel(self, event):
        # Cross-platform mouse wheel support
        try:
            if event.num == 4:
                # Linux scroll up
                self.canvas.yview_scroll(-3, 'units')
            elif event.num == 5:
                # Linux scroll down
                self.canvas.yview_scroll(3, 'units')
            else:
                # Windows / Mac (event.delta) -> typically multiples of 120
                delta = int(event.delta / 120) if event.delta else 0
                self.canvas.yview_scroll(-3 * delta, 'units')
        except Exception:
            pass


def main():
    app = PlateGridApp()
    app.mainloop()


if __name__ == '__main__':
    main()
