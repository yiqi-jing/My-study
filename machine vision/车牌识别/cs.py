import os
import sys
import re
import numpy as np
import glob
import cv2
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import threading
import time
from hyperlpr import HyperLPR_plate_recognition

# 解决numpy兼容问题
if not hasattr(np, 'int'):
    np.int = np.int64

class LicensePlateRecognizer:
    def __init__(self, root):
        self.root = root
        self.root.title("车牌识别系统")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # 设置中文字体
        self.style = ttk.Style()
        self.style.configure("Treeview.Heading", font=("SimHei", 10, "bold"))
        self.style.configure("Treeview", font=("SimHei", 10), rowheight=25)
        
        # 变量初始化
        self.image_paths = []
        self.current_image_index = -1
        self.processing = False
        self.stop_processing_flag = False
        
        self.init_ui()
        
    def init_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧控制面板
        control_frame = ttk.LabelFrame(main_frame, text="控制", padding="10")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # 按钮
        btn_select_single = ttk.Button(control_frame, text="选择单张图片", command=self.select_single_image)
        btn_select_single.pack(fill=tk.X, pady=(0, 5))
        
        btn_select_folder = ttk.Button(control_frame, text="选择图片文件夹", command=self.select_image_folder)
        btn_select_folder.pack(fill=tk.X, pady=(0, 5))
        
        btn_start_recognize = ttk.Button(control_frame, text="开始识别", command=self.start_recognition)
        btn_start_recognize.pack(fill=tk.X, pady=(0, 5))
        
        btn_stop = ttk.Button(control_frame, text="停止处理", command=self.stop_processing)
        btn_stop.pack(fill=tk.X, pady=(0, 5))
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(control_frame, variable=self.progress_var, length=200, mode='determinate')
        progress_bar.pack(fill=tk.X, pady=(20, 5))
        
        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(control_frame, textvariable=self.status_var)
        status_label.pack(fill=tk.X, pady=(5, 20))
        
        # 右侧显示区域
        display_frame = ttk.Frame(main_frame)
        display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 图片显示区域
        image_frame = ttk.LabelFrame(display_frame, text="图片与车牌", padding="10")
        image_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.image_canvas = tk.Canvas(image_frame, bg="#f0f0f0")
        self.image_canvas.pack(fill=tk.BOTH, expand=True)
        
        # 结果表格 - 移除颜色列
        result_frame = ttk.LabelFrame(display_frame, text="识别结果", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("图片名称", "车牌号码", "状态")
        self.result_tree = ttk.Treeview(result_frame, columns=columns, show="headings")
        
        # 设置列宽和标题
        self.result_tree.column("图片名称", width=200)
        self.result_tree.column("车牌号码", width=150)
        self.result_tree.column("状态", width=150)
        
        for col in columns:
            self.result_tree.heading(col, text=col)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_tree.yview)
        self.result_tree.configure(yscroll=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_tree.pack(fill=tk.BOTH, expand=True)
        
        # 绑定双击事件查看图片
        self.result_tree.bind("<Double-1>", self.on_tree_item_double_click)
    
    def select_single_image(self):
        """选择单张图片"""
        file_path = filedialog.askopenfilename(
            filetypes=[("图片文件", "*.jpg;*.jpeg;*.png;*.bmp;*.JPG;*.JPEG;*.PNG;*.BMP")]
        )
        if file_path:
            self.image_paths = [file_path]
            self.clear_results()
            self.status_var.set(f"已选择 1 张图片")
    
    def select_image_folder(self):
        """选择图片文件夹"""
        folder = filedialog.askdirectory()
        if folder:
            self.image_paths = self.get_image_paths(folder)
            self.clear_results()
            self.status_var.set(f"已选择 {len(self.image_paths)} 张图片")
    
    def get_image_paths(self, folder):
        """获取文件夹中的所有图片路径"""
        paths = []
        for ext in ('.jpg', '.jpeg', '.png', '.bmp'):
            paths.extend(glob.glob(os.path.join(folder, f'*{ext}'), recursive=False))
            paths.extend(glob.glob(os.path.join(folder, f'*{ext.upper()}'), recursive=False))
        return sorted(list(set(paths)))
    
    def start_recognition(self):
        """开始识别车牌"""
        if not self.image_paths:
            messagebox.showwarning("警告", "请先选择图片或图片文件夹")
            return
        
        if self.processing:
            messagebox.showinfo("提示", "正在处理中，请等待完成或停止当前处理")
            return
        
        self.clear_results()
        self.processing = True
        self.stop_processing_flag = False
        self.progress_var.set(0)
        
        # 在新线程中处理，避免界面卡顿
        threading.Thread(target=self.process_images, daemon=True).start()
    
    def stop_processing(self):
        """停止处理图片"""
        if self.processing:
            self.stop_processing_flag = True
            self.status_var.set("正在停止处理...")
    
    def process_images(self):
        """处理所有图片"""
        total = len(self.image_paths)
        success_count = 0
        
        for i, img_path in enumerate(self.image_paths):
            if self.stop_processing_flag:
                self.processing = False
                self.status_var.set("已停止处理")
                return
            
            # 更新进度
            progress = (i + 1) / total * 100
            self.progress_var.set(progress)
            self.status_var.set(f"正在处理 {i+1}/{total}：{os.path.basename(img_path)}")
            
            # 识别车牌
            plate, status = self.recognize_plate(img_path)
            
            # 更新结果表格
            img_name = os.path.basename(img_path)
            self.root.after(0, self.add_result, img_name, plate, status)
            
            # 显示当前处理的图片
            if i == 0 or self.current_image_index != i:
                self.current_image_index = i
                self.root.after(0, self.display_image_with_plate, img_path, plate)
            
            if status == "识别成功":
                success_count += 1
            
            # 短暂延迟，让界面有时间更新
            time.sleep(0.01)
        
        # 处理完成
        self.processing = False
        self.status_var.set(f"处理完成，共 {total} 张，成功 {success_count} 张，识别率 {success_count/total:.2%}")
    
    def recognize_plate(self, image_path):
        """识别单张图片的车牌"""
        try:
            if not os.path.exists(image_path):
                return None, "文件不存在"
            
            if not image_path.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                return None, "非图片格式"
            
            image = cv2.imread(image_path)
            if image is None:
                return None, "无法读取图片"
            
            # 增强图像特征
            enhanced_img = self.enhance_image_for_plate(image)
            
            # 多尺度检测
            scales = [0.8, 1.0, 1.2]
            all_results = []
            
            for scale in scales:
                if scale != 1.0:
                    resized = cv2.resize(enhanced_img, (0, 0), fx=scale, fy=scale)
                else:
                    resized = enhanced_img.copy()
                
                results = HyperLPR_plate_recognition(resized)
                if results:
                    # 转换回原始坐标并兼容不同返回格式
                    for result in results:
                        if len(result) >= 3:  # 只关注前三个元素：车牌、置信度、位置
                            plate_str, conf, (x1, y1, x2, y2) = result[:3]
                            
                            if scale != 1.0:
                                x1_scaled = int(x1 / scale)
                                y1_scaled = int(y1 / scale)
                                x2_scaled = int(x2 / scale)
                                y2_scaled = int(y2 / scale)
                                all_results.append((plate_str, conf, (x1_scaled, y1_scaled, x2_scaled, y2_scaled)))
                            else:
                                all_results.append((plate_str, conf, (x1, y1, x2, y2)))
            
            if not all_results:
                return None, "未识别到车牌"
            
            # 选择置信度最高的结果
            best_result = max(all_results, key=lambda x: x[1])
            plate_str, _, _ = best_result
            processed_plate = self.postprocess_plate(plate_str)
            
            return processed_plate, "识别成功"
            
        except Exception as e:
            return None, f"识别错误：{str(e)}"
    
    def postprocess_plate(self, plate_str):
        """修正字符错误，统一格式"""
        plate_str = re.sub(r'[\s·-]', '', plate_str).upper()  # 去除分隔符
        # 常见字符错误修正
        char_correction = {
        }
        for wrong, right in char_correction.items():
            plate_str = plate_str.replace(wrong, right)
        return plate_str
    
    def enhance_image_for_plate(self, image):
        """对车牌区域进行颜色和对比度增强"""
        # 转换为HSV空间
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        
        # 增强蓝色通道（蓝牌）
        lower_blue = np.array([90, 40, 40])
        upper_blue = np.array([130, 255, 255])
        mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
        s[mask_blue > 0] = np.clip(s[mask_blue > 0] + 30, 0, 255)
        
        # 增强绿色通道（新能源绿牌）
        lower_green = np.array([40, 40, 50])
        upper_green = np.array([80, 255, 255])
        mask_green = cv2.inRange(hsv, lower_green, upper_green)
        v[mask_green > 0] = np.clip(v[mask_green > 0] + 20, 0, 255)
        
        # 合并通道并转回BGR
        enhanced_hsv = cv2.merge([h, s, v])
        return cv2.cvtColor(enhanced_hsv, cv2.COLOR_HSV2BGR)
    
    def display_image_with_plate(self, image_path, plate_number):
        """显示图片并标记车牌位置"""
        try:
            # 清空画布
            self.image_canvas.delete("all")
            
            # 读取图片
            image = cv2.imread(image_path)
            if image is None:
                self.image_canvas.create_text(100, 100, text="无法加载图片", font=("SimHei", 12))
                return
            
            # 转换为RGB格式
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # 再次识别以获取车牌位置（用于显示）
            enhanced_img = self.enhance_image_for_plate(image)
            results = HyperLPR_plate_recognition(enhanced_img)
            
            # 绘制车牌框
            plate_region = None  # 初始化车牌区域变量
            if results:
                # 兼容不同返回格式
                best_result = None
                max_conf = -1
                for result in results:
                    if len(result) >= 3:
                        conf = result[1]
                        if conf > max_conf:
                            max_conf = conf
                            best_result = result
                if best_result:
                    _, _, (x1, y1, x2, y2) = best_result[:3]
                    cv2.rectangle(image_rgb, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    
                    # 提取车牌区域
                    plate_region = image_rgb[y1:y2, x1:x2]
            
            # 调整图片大小以适应画布
            canvas_width = self.image_canvas.winfo_width()
            canvas_height = self.image_canvas.winfo_height()
            
            # 如果画布还没渲染，使用默认尺寸
            if canvas_width < 100:
                canvas_width = 600
            if canvas_height < 100:
                canvas_height = 400
                
            # 计算缩放比例
            h, w = image_rgb.shape[:2]
            scale = min(canvas_width / w, canvas_height / h)
            new_w = int(w * scale)
            new_h = int(h * scale)
            
            # 缩放图片
            resized_img = cv2.resize(image_rgb, (new_w, new_h))
            
            # 转换为ImageTk格式
            pil_img = Image.fromarray(resized_img)
            tk_img = ImageTk.PhotoImage(image=pil_img)
            
            # 存储图片引用，防止被垃圾回收
            self.current_tk_image = tk_img
            
            # 在画布上显示图片
            x_pos = (canvas_width - new_w) // 2
            y_pos = (canvas_height - new_h) // 2
            self.image_canvas.create_image(x_pos, y_pos, anchor=tk.NW, image=tk_img)
            
            # 显示识别结果
            if plate_number:
                result_text = f"车牌号码: {plate_number}"
                self.image_canvas.create_text(
                    canvas_width // 2, y_pos + new_h + 20, 
                    text=result_text, 
                    font=("SimHei", 12, "bold"),
                    fill="blue"
                )
                
            # 显示车牌区域（如果有）
            if plate_region is not None:
                # 调整车牌区域大小以便显示
                plate_h, plate_w = plate_region.shape[:2]
                plate_scale = min(200 / plate_w, 100 / plate_h)
                plate_new_w = int(plate_w * plate_scale)
                plate_new_h = int(plate_h * plate_scale)
                
                resized_plate = cv2.resize(plate_region, (plate_new_w, plate_new_h))
                pil_plate = Image.fromarray(resized_plate)
                tk_plate = ImageTk.PhotoImage(image=pil_plate)
                
                self.current_plate_image = tk_plate
                
                self.image_canvas.create_image(
                    canvas_width // 2, y_pos + new_h + 50, 
                    anchor=tk.NW, 
                    image=tk_plate
                )
                
        except Exception as e:
            self.image_canvas.create_text(100, 100, text=f"显示错误: {str(e)}", font=("SimHei", 12))
    
    def add_result(self, img_name, plate, status):
        """添加结果到表格"""
        self.result_tree.insert("", tk.END, values=(img_name, plate or "", status))
    
    def clear_results(self):
        """清空结果表格"""
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        self.image_canvas.delete("all")
        self.current_image_index = -1
    
    def on_tree_item_double_click(self, event):
        """双击表格项查看图片"""
        selected_item = self.result_tree.selection()
        if not selected_item:
            return
            
        item = self.result_tree.item(selected_item[0])
        img_name = item["values"][0]
        
        # 找到对应的图片路径
        for path in self.image_paths:
            if os.path.basename(path) == img_name:
                plate = item["values"][1]
                self.display_image_with_plate(path, plate)
                break

if __name__ == "__main__":
    root = tk.Tk()
    app = LicensePlateRecognizer(root)
    root.mainloop()