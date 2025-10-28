import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import time
import cv2
import numpy as np
import easyocr

class LicensePlateRecognizer:
    def __init__(self, root):
        self.root = root
        self.root.title("车牌识别系统 - 本地图片识别")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 初始化EasyOCR识别器（只加载中文和英文，速度更快）
        self.reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)  # 禁用GPU，避免依赖
        
        # 设置中文字体
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("SimHei", 10))
        self.style.configure("TButton", font=("SimHei", 10))
        self.style.configure("Header.TLabel", font=("SimHei", 16, "bold"))
        
        # 初始化变量
        self.current_image = None  # 存储当前打开的图像
        self.tk_image = None       # 存储Tkinter显示的图像
        self.file_path = ""        # 存储图片路径
        
        # 创建UI
        self._create_widgets()
    
    def _create_widgets(self):
        # 标题
        header = ttk.Label(self.root, text="车牌识别系统", style="Header.TLabel")
        header.pack(pady=10)
        
        # 主框架
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧图像显示区
        left_frame = ttk.LabelFrame(main_frame, text="图片预览", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.canvas = tk.Canvas(left_frame, bg="#f0f0f0", width=400, height=300)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 右侧操作与结果区
        right_frame = ttk.LabelFrame(main_frame, text="操作与结果", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 按钮区
        btn_frame = ttk.Frame(right_frame)
        btn_frame.pack(fill=tk.X, pady=20)
        
        self.select_btn = ttk.Button(btn_frame, text="选择本地图片", command=self.select_image)
        self.select_btn.pack(fill=tk.X, pady=10, ipady=5)
        
        self.recognize_btn = ttk.Button(btn_frame, text="开始识别车牌", command=self.recognize_plate)
        self.recognize_btn.pack(fill=tk.X, pady=10, ipady=5)
        self.recognize_btn.config(state=tk.DISABLED)
        
        # 结果显示区
        result_frame = ttk.LabelFrame(right_frame, text="识别结果", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        ttk.Label(result_frame, text="识别到的车牌号码：", font=("SimHei", 11)).pack(anchor=tk.W, pady=5)
        self.result_var = tk.StringVar()
        self.result_entry = ttk.Entry(result_frame, textvariable=self.result_var, 
                                      font=("SimHei", 14, "bold"), state="readonly")
        self.result_entry.pack(fill=tk.X, pady=5)
        
        ttk.Label(result_frame, text="识别耗时：", font=("SimHei", 11)).pack(anchor=tk.W, pady=5)
        self.time_var = tk.StringVar()
        self.time_entry = ttk.Entry(result_frame, textvariable=self.time_var, state="readonly")
        self.time_entry.pack(fill=tk.X, pady=5)
        
        ttk.Label(result_frame, text="识别置信度：", font=("SimHei", 11)).pack(anchor=tk.W, pady=5)
        self.confidence_var = tk.StringVar()
        self.confidence_entry = ttk.Entry(result_frame, textvariable=self.confidence_var, state="readonly")
        self.confidence_entry.pack(fill=tk.X, pady=5)
        
        # 状态提示
        self.status_var = tk.StringVar(value="请选择一张包含车牌的图片")
        self.status_label = ttk.Label(right_frame, textvariable=self.status_var, foreground="green")
        self.status_label.pack(side=tk.BOTTOM, pady=10, anchor=tk.W)
    
    def select_image(self):
        """选择并显示本地图片"""
        file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[("图像文件", "*.jpg;*.jpeg;*.png;*.bmp"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                file_name = file_path.split('/')[-1].split('\\')[-1]
                self.status_var.set(f"正在加载图片: {file_name}")
                self.root.update()
                
                # 加载图片
                pil_image = Image.open(file_path)
                self.current_image = cv2.imread(file_path)
                self.file_path = file_path
                
                # 显示图片
                self._display_image(pil_image)
                
                # 重置结果
                self.result_var.set("")
                self.time_var.set("")
                self.confidence_var.set("")
                
                self.recognize_btn.config(state=tk.NORMAL)
                self.status_var.set("图片加载完成，请点击开始识别")
                
            except Exception as e:
                messagebox.showerror("错误", f"图片加载失败: {str(e)}")
                self.status_var.set("图片加载失败，请重新选择")
                self.current_image = None
                self.recognize_btn.config(state=tk.DISABLED)
    
    def recognize_plate(self):
        """车牌识别核心逻辑"""
        # 修复：正确判断图像数组是否为空
        if self.current_image is None or self.current_image.size == 0 or not self.file_path:
            messagebox.showwarning("警告", "请先选择有效的图片")
            return
        
        self.recognize_btn.config(state=tk.DISABLED)
        self.status_var.set("正在识别，请稍候...")
        self.root.update()
        
        try:
            start_time = time.time()
            
            # 用EasyOCR识别
            results = self.reader.readtext(self.file_path)
            
            elapsed_time = time.time() - start_time
            
            if results:
                # 筛选车牌候选（7-8位字符，含字母和数字）
                plate_candidates = []
                for (bbox, text, confidence) in results:
                    # 过滤车牌格式：通常是省份简称(1字)+字母(1)+字母数字(5)，共7位
                    if 5 <= len(text) <= 8 and any(c.isdigit() for c in text) and any(c.isalpha() for c in text):
                        plate_candidates.append((text, confidence, bbox))
                
                if plate_candidates:
                    # 选置信度最高的结果
                    best_plate = max(plate_candidates, key=lambda x: x[1])
                    plate_num, conf, bbox = best_plate
                    
                    # 绘制车牌框和文字
                    processed_img = self.current_image.copy()
                    pts = np.array(bbox, np.int32).reshape((-1, 1, 2))
                    cv2.polylines(processed_img, [pts], True, (0, 255, 0), 2)
                    cv2.putText(processed_img, plate_num, (pts[0][0][0], pts[0][0][1]-10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                    
                    # 更新结果
                    self.result_var.set(plate_num)
                    self.time_var.set(f"{elapsed_time:.3f} 秒")
                    self.confidence_var.set(f"{conf:.4f}")
                    
                    # 显示处理后的图片
                    processed_img = cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB)
                    self._display_image(Image.fromarray(processed_img))
                    
                    self.status_var.set("识别完成")
                else:
                    self.result_var.set("未识别到车牌")
                    self.time_var.set(f"{elapsed_time:.3f} 秒")
                    self.status_var.set("未找到符合车牌特征的内容")
            else:
                self.result_var.set("未识别到任何文字")
                self.time_var.set(f"{elapsed_time:.3f} 秒")
                self.status_var.set("图片中未检测到文字")
                
        except Exception as e:
            messagebox.showerror("识别错误", f"出错：{str(e)}")
            self.status_var.set("识别失败，请重试")
        finally:
            self.recognize_btn.config(state=tk.NORMAL)
    
    def _display_image(self, image):
        """自适应显示图片"""
        canvas_w = self.canvas.winfo_width() or 400
        canvas_h = self.canvas.winfo_height() or 300
        
        # 保持比例缩放
        image.thumbnail((canvas_w, canvas_h))
        self.tk_image = ImageTk.PhotoImage(image=image)
        
        # 居中显示
        x = (canvas_w - image.width) // 2
        y = (canvas_h - image.height) // 2
        self.canvas.delete("all")
        self.canvas.create_image(x, y, anchor=tk.NW, image=self.tk_image)

if __name__ == "__main__":
    root = tk.Tk()
    app = LicensePlateRecognizer(root)
    root.mainloop()