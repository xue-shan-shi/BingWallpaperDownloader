import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import requests
import threading
from pathlib import Path
import sys
import datetime

class BingWallpaperDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("必应壁纸下载器")
        self.root.geometry("700x860")
        self.root.minsize(700, 860)
        
        # 设置窗口缩放响应
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        
        # 设置窗口图标（如果有的话）
        # self.root.iconbitmap('1.ico')
        
        # 初始化变量
        self.app_name = "必应壁纸下载器"
        self.version = "v1.5"        
        self.allow_download_min = "20180911"
        self.json_file = "Bing_zh-CN_all.json"
        self.json_url = "https://cdn.jsdelivr.net/gh/Zhu-junwei/bing-wallpaper-archive/Bing_zh-CN_all.json"
        
        self.min_date = ""
        self.max_date = ""
        self.start_date = ""
        self.end_date = ""
        self.resolution = "原图"
        self.custom_width = ""
        self.custom_height = ""
        self.download_folder = ""
        self.thread_count = 8  # 默认线程数
        self.total_images = 0
        self.downloaded_count = 0        
        # 创建GUI
        self.create_widgets()
        
        # 尝试加载JSON文件
        self.load_json_file()
        
    def create_widgets(self):
        # 创建样式
        self.create_styles()
        
        # 主容器，支持缩放
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky="wens", padx=15, pady=15)
        
        # 配置主容器的行列权重
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(9, weight=1)  # 让状态标签下方有弹性空间
        
        # 标题
        title_label = ttk.Label(main_frame, text="必应壁纸下载器", 
                                foreground="#2E86AB", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky="we")
        title_label.configure(anchor="center")
        
        # 日期选择
        date_frame = ttk.LabelFrame(main_frame, text="📆 日期选择", padding="12", 
                                    style="Custom.TLabelframe")
        date_frame.grid(row=1, column=0, columnspan=2, sticky="we", pady=(0, 12))
        date_frame.columnconfigure(1, weight=1)
        date_frame.columnconfigure(3, weight=1)
        
        # 可下载范围显示
        self.range_label = ttk.Label(date_frame, text="正在加载日期范围...", 
                                     foreground="#555555")
        self.range_label.grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 8))
        
        ttk.Label(date_frame, text="开始日期:").grid(row=1, column=0, padx=(0, 8), sticky=tk.W)
        self.start_date_entry = ttk.Entry(date_frame, width=15)
        self.start_date_entry.grid(row=1, column=1, padx=(0, 20), sticky="we")
        
        ttk.Label(date_frame, text="结束日期:").grid(row=1, column=2, padx=(0, 8), sticky=tk.W)
        self.end_date_entry = ttk.Entry(date_frame, width=15)
        self.end_date_entry.grid(row=1, column=3, padx=(0, 0), sticky="we")
        
        # 分辨率选择
        res_frame = ttk.LabelFrame(main_frame, text="分辨率选择", padding="12", 
                                   style="Custom.TLabelframe")
        res_frame.grid(row=3, column=0, columnspan=2, sticky="we", pady=(0, 12))
        res_frame.columnconfigure(0, weight=1)
        res_frame.columnconfigure(1, weight=1)
        
        self.res_var = tk.StringVar(value="1")
        resolutions = [
            ("原图", "1"),
            ("4K (3840x2160)", "2"),
            ("2K (2560x1440)", "3"),
            ("1080P (1920x1080)", "4")
        ]
        
        for i, (text, value) in enumerate(resolutions):
            rb = ttk.Radiobutton(res_frame, text=text, variable=self.res_var, 
                                value=value)
            rb.grid(row=i//2, column=i%2, sticky=tk.W, pady=4, padx=(0, 10))
            
        # 自定义分辨率输入
        custom_frame = ttk.Frame(res_frame)
        custom_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(8, 0), padx=(20, 0))
        
        # 将自定义分辨率选项和输入框放在同一行
        custom_radio = ttk.Radiobutton(custom_frame, text="⚙️ 自定义分辨率", variable=self.res_var, 
                                      value="5")
        custom_radio.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Label(custom_frame, text="宽度:").pack(side=tk.LEFT, padx=(0, 5))
        self.width_entry = ttk.Entry(custom_frame, width=10, state="disabled")
        self.width_entry.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Label(custom_frame, text="高度:").pack(side=tk.LEFT, padx=(0, 5))
        self.height_entry = ttk.Entry(custom_frame, width=10, state="disabled")
        self.height_entry.pack(side=tk.LEFT)

        self.res_var.trace_add('write', self.on_resolution_change)
        
        # 下载位置
        folder_frame = ttk.LabelFrame(main_frame, text="⚙️ 下载设置", padding="12", 
                                      style="Custom.TLabelframe")
        folder_frame.grid(row=4, column=0, columnspan=2, sticky="we", pady=(0, 12))
        folder_frame.columnconfigure(0, weight=1)
        
        folder_button_frame = ttk.Frame(folder_frame)
        folder_button_frame.grid(row=0, column=0, sticky="we")
        folder_button_frame.columnconfigure(1, weight=1)
        
        ttk.Label(folder_button_frame, text="下载位置:").grid(row=0, column=0, sticky=tk.W, pady=(0, 8))
        
        self.folder_label = ttk.Label(folder_button_frame, text="", wraplength=600, 
                                     foreground="#555555")
        self.folder_label.grid(row=0, column=1, sticky=tk.W, pady=(0, 8), padx=(10, 0))
        
        ttk.Button(folder_button_frame, text="📂 选择文件夹", command=self.select_folder).grid(row=0, column=2, padx=(10, 0))
        
        # 多线程设置
        thread_frame = ttk.Frame(folder_frame)
        thread_frame.grid(row=1, column=0, sticky="we", pady=(10, 0))
        thread_frame.columnconfigure(1, weight=1)
        
        ttk.Label(thread_frame, text="线程数:").grid(row=0, column=0, sticky=tk.W)
        
        self.thread_var = tk.StringVar(value="8")
        thread_spinbox = ttk.Spinbox(thread_frame, from_=1, to=32, width=10, textvariable=self.thread_var)
        thread_spinbox.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(thread_frame, text="(1-32, 默认8)").grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
        
        # 设置默认下载位置
        self.set_default_folder()
        
        # 说明文本
        note_frame = ttk.LabelFrame(main_frame, text="ℹ️ 说明", padding="12", 
                                    style="Custom.TLabelframe")
        note_frame.grid(row=5, column=0, columnspan=2, sticky="we", pady=(0, 12))
        note_frame.columnconfigure(0, weight=1)
        
        notes = [
            "• 20190510之前的壁纸只能下载1080P分辨率",
            "• 图片数据源：https://github.com/Zhu-junwei/bing-wallpaper-archive",
            "• 缺少JSON文件时程序会自动下载"
        ]
        
        for i, note in enumerate(notes):
            ttk.Label(note_frame, text=note, 
                     foreground="#666666").grid(row=i, column=0, sticky=tk.W, pady=2)
        
        # 进度条和状态
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=6, column=0, columnspan=2, sticky="we", pady=(0, 8))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress = ttk.Progressbar(progress_frame, mode='determinate', 
                                       style="Custom.Horizontal.TProgressbar")
        self.progress.grid(row=0, column=0, sticky="we")
        
        # 状态和统计信息
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=7, column=0, columnspan=2, sticky="we", pady=(0, 15))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_label = ttk.Label(status_frame, text="就绪", 
                                     foreground="#0066CC")
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=2, sticky="we", pady=(0, 10))
        
        # 创建内部按钮框架并居中
        buttons_inner_frame = ttk.Frame(button_frame)
        buttons_inner_frame.pack(expand=True)
        
        ttk.Button(buttons_inner_frame, text="🚀 开始下载壁纸", command=self.start_download, 
                  style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_inner_frame, text="❌ 退出", command=self.root.quit).pack(side=tk.LEFT, padx=5)
        
    def create_styles(self):
        """创建自定义样式"""
        style = ttk.Style()
        
        # 设置主题为现代主题
        if 'clam' in style.theme_names():
            style.theme_use('clam')
        elif 'alt' in style.theme_names():
            style.theme_use('alt')
        
        # 配置颜色方案（现代深蓝主题）
        bg_color = "#F5F7FA"
        fg_color = "#2C3E50"
        accent_color = "#2E86AB"
        accent_light = "#A23B72"
        border_color = "#D1D5DB"
        
        # 配置LabelFrame样式
        style.configure("Custom.TLabelframe", 
                       background=bg_color,
                       foreground=fg_color,
                       borderwidth=1,
                       relief="solid",
                       padding=10)
        style.configure("Custom.TLabelframe.Label",
                       background=bg_color,
                       foreground=accent_color,
                       padding=5)
        
        # 配置Entry样式
        style.configure("TEntry",
                       padding=6,
                       fieldbackground="white",
                       foreground=fg_color)
        
        # 配置Label样式
        style.configure("TLabel",
                       background=bg_color,
                       foreground=fg_color)
        
        # 配置Radiobutton样式
        style.configure("TRadiobutton",
                       background=bg_color,
                       foreground=fg_color,
                       padding=5)
        
        # 配置Button样式
        style.configure("TButton",
                       padding=8)
        
        style.map("TButton",
                 foreground=[('active', 'white')],
                 background=[('active', accent_color)])
        
        # 配置强调按钮样式
        style.configure("Accent.TButton",
                       padding=8,
                       foreground="white")
        
        style.map("Accent.TButton",
                 background=[('!active', accent_color),
                            ('active', accent_light)],
                 foreground=[('!active', 'white'),
                            ('active', 'white')])
        
        # 配置Progressbar样式
        style.configure("Custom.Horizontal.TProgressbar",
                       background=accent_color,
                       troughcolor=border_color,
                       bordercolor=border_color,
                       lightcolor=accent_color,
                       darkcolor=accent_color,
                       padding=2)
        
        # 配置主Frame
        style.configure("TFrame",
                       background=bg_color)
        
        # 配置主窗口背景
        self.root.configure(bg=bg_color)
        
    def on_resolution_change(self, *args):
        """处理分辨率选择变化"""
        if self.res_var.get() == "5":
            self.width_entry.config(state="normal")
            self.height_entry.config(state="normal")
        else:
            self.width_entry.config(state="disabled")
            self.height_entry.delete(0, tk.END)
            self.height_entry.insert(0, "")
            self.width_entry.delete(0, tk.END)
            self.width_entry.insert(0, "")
            
    def set_default_folder(self):
        """设置默认下载文件夹（当前目录下的Bing壁纸文件夹）"""
        current_dir = Path.cwd()
        self.download_folder = str(current_dir / "Bing壁纸")
        self.folder_label.config(text=self.download_folder)
        
    def select_folder(self):
        """选择下载文件夹"""
        folder = filedialog.askdirectory(title="请选择必应壁纸下载位置")
        if folder:
            self.download_folder = folder
            self.folder_label.config(text=self.download_folder)
            
    def load_json_file(self):
        """加载或下载JSON文件"""
        # 检查文件是否存在
        if os.path.exists(self.json_file):
            # 文件存在，检查日期
            try:
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 检查最新的图片日期是否为今天
                if data['images'] and data['images'][0]['enddate'] == datetime.datetime.now().strftime('%Y%m%d'):
                    # 如果是最新的，直接使用
                    pass
                else:
                    # 如果不是最新的，重新下载
                    if not self._download_json():
                        return False
            except Exception as e:
                self.status_label.config(text=f"JSON文件读取失败: {str(e)}", foreground="#FF0000")
                return False
        else:
            # 文件不存在，下载
            if not self._download_json():
                return False
            
        # 解析JSON文件
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            dates = [img['enddate'] for img in data['images']]
            self.min_date = min(dates)
            self.max_date = max(dates)
            
            # 确保最小日期不小于允许的最小日期
            if self.min_date < self.allow_download_min:
                self.min_date = self.allow_download_min
                
            # 更新UI显示
            self.range_label.config(text=f"可下载范围: {self.min_date} - {self.max_date}")
            self.start_date_entry.delete(0, tk.END)
            self.start_date_entry.insert(0, self.min_date)
            self.end_date_entry.delete(0, tk.END)
            self.end_date_entry.insert(0, self.max_date)
            
            self.status_label.config(text="JSON文件加载成功", foreground="#00AA00")
            return True
            
        except Exception as e:
            self.status_label.config(text=f"JSON解析失败: {str(e)}", foreground="#FF0000")
            return False

    def _download_json(self):
        """下载JSON文件"""
        self.status_label.config(text="正在下载JSON文件...", foreground="#FF9900")
        self.root.update()
        
        try:
            response = requests.get(self.json_url, timeout=30)
            if response.status_code == 200:
                with open(self.json_file, 'wb') as f:
                    f.write(response.content)
                self.status_label.config(text="JSON文件下载成功", foreground="#00AA00")
            else:
                self.status_label.config(text="JSON文件下载失败", foreground="#FF0000")
                return False
        except Exception as e:
            self.status_label.config(text=f"下载失败: {str(e)}", foreground="#FF0000")
            return False
        return True
            
    def validate_inputs(self):
        """验证输入参数"""
        # 获取日期
        self.start_date = self.start_date_entry.get().strip()
        self.end_date = self.end_date_entry.get().strip()
        
        if not self.start_date:
            self.start_date = self.min_date
            self.start_date_entry.delete(0, tk.END)
            self.start_date_entry.insert(0, self.start_date)
            
        if not self.end_date:
            self.end_date = self.max_date
            self.end_date_entry.delete(0, tk.END)
            self.end_date_entry.insert(0, self.end_date)
            
        # 验证日期格式和范围
        try:
            if not (self.start_date.isdigit() and len(self.start_date) == 8):
                raise ValueError("开始日期格式错误")
            if not (self.end_date.isdigit() and len(self.end_date) == 8):
                raise ValueError("结束日期格式错误")
                
            if self.start_date < self.min_date:
                raise ValueError(f"开始日期不能早于 {self.min_date}")
            if self.end_date > self.max_date:
                raise ValueError(f"结束日期不能晚于 {self.max_date}")
            if self.start_date > self.end_date:
                raise ValueError("开始日期不能晚于结束日期")
                
        except ValueError as e:
            messagebox.showerror("输入错误", str(e))
            return False
            
        # 验证分辨率选择
        res_choice = self.res_var.get()
        if res_choice == "5":
            # 自定义分辨率
            self.custom_width = self.width_entry.get().strip()
            self.custom_height = self.height_entry.get().strip()
            
            if not (self.custom_width.isdigit() and self.custom_height.isdigit()):
                messagebox.showerror("输入错误", "自定义分辨率必须为数字")
                return False
                
            self.resolution = f"{self.custom_width}x{self.custom_height}"
            
        elif res_choice == "2":
            self.resolution = "3840x2160"
        elif res_choice == "3":
            self.resolution = "2560x1440"
        elif res_choice == "4":
            self.resolution = "1920x1080"
        else:
            self.resolution = "原图"
            
        # 验证下载文件夹
        if not self.download_folder:
            messagebox.showerror("错误", "请选择下载文件夹")
            return False
            
        # 验证线程数
        try:
            self.thread_count = int(self.thread_var.get())
            if not (1 <= self.thread_count <= 32):
                raise ValueError("线程数必须在1-32之间")
        except ValueError as e:
            if "invalid literal" in str(e):
                messagebox.showerror("输入错误", "线程数必须是整数")
            else:
                messagebox.showerror("输入错误", str(e))
            return False
            
        return True
        
    def get_image_urls(self):
        """获取图片URL列表"""
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            images = []
            for img in data['images']:
                if self.start_date <= img['enddate'] <= self.end_date:
                    images.append(img)
                    
            return images
            
        except Exception as e:
            self.status_label.config(text=f"解析图片失败: {str(e)}", foreground="#FF0000")
            return []
            
    def download_thread(self):
        """下载线程"""
        try:
            # 获取图片列表
            self.status_label.config(text="正在解析图片信息...", foreground="#0066CC")
            self.root.update()
            
            images = self.get_image_urls()
            total = len(images)
            
            if total == 0:
                self.status_label.config(text="没有找到符合条件的图片", foreground="#FF9900")
                return
                
            # 创建下载文件夹
            os.makedirs(self.download_folder, exist_ok=True)
            
            # 重置进度
            self.progress['value'] = 0
            self.downloaded_count = 0
            failed_count = 0  # 添加失败计数
            
            self.status_label.config(text=f"开始下载 {total} 张图片 (线程数: {self.thread_count})...", foreground="#0066CC")
            self.root.update()
            
            # 使用线程池而不是为每个图片创建线程
            from concurrent.futures import ThreadPoolExecutor, as_completed
            
            # 需要下载的图片列表
            download_tasks = []
            
            # 预处理：创建文件夹并确定需要下载的图片
            for img in images:
                # 创建年份文件夹
                year = img['enddate'][:4]
                year_folder = os.path.join(self.download_folder, year)
                os.makedirs(year_folder, exist_ok=True)
                
                # 生成文件名
                name = f"{img['enddate']}_{img['urlbase'][7:]}.jpg"
                save_path = os.path.join(year_folder, name)
                
                # 如果文件已存在，跳过
                if os.path.exists(save_path):
                    self.downloaded_count += 1
                    self.update_progress(self.downloaded_count + failed_count, total)
                else:
                    download_tasks.append((img, save_path))
            
            # 使用线程池执行下载任务
            with ThreadPoolExecutor(max_workers=self.thread_count) as executor:
                # 提交所有下载任务
                future_to_img = {
                    executor.submit(self.download_image, img, save_path, total): (img, save_path) 
                    for img, save_path in download_tasks
                }
                
                # 处理完成的任务
                for future in as_completed(future_to_img):
                    try:
                        success = future.result()
                        if not success:
                            failed_count += 1
                    except Exception as e:
                        failed_count += 1
                        print(f"下载过程中发生异常: {str(e)}")
            
            # 下载完成
            success_count = self.downloaded_count
            self.status_label.config(
                text=f"下载完成！成功: {success_count}, 失败: {failed_count}, 总计: {total}", 
                foreground="#00AA00" if failed_count == 0 else "#FF9900"
            )
            messagebox.showinfo(
                "下载完成", 
                f"壁纸下载完成！\n总计: {total} 张\n成功: {success_count} 张\n失败: {failed_count} 张"
            )
            
        except Exception as e:
            self.status_label.config(text=f"下载过程出错: {str(e)}", foreground="#FF0000")
            messagebox.showerror("下载错误", str(e))

    def download_image(self, img, save_path, total):
        """下载单张图片"""
        try:
            # 构建URL
            if int(img['enddate']) < 20190510:
                url = img['url']
            else:
                url = f"https://www.bing.com{img['urlbase']}_UHD.jpg&rf=LaDigue_UHD.jpg&pid=hp"
                
            # 添加分辨率参数（如果需要）
            if self.resolution != "原图" and int(img['enddate']) >= 20190510:
                if self.res_var.get() == "5":
                    w, h = self.resolution.split('x')
                else:
                    w, h = self.resolution.split('x')
                    w = w[:-1] if w.endswith('x') else w
                    
                url += f"&w={w}&h={h}&rs=1&c=4"
                
            # 下载图片
            response = requests.get(url, stream=True, timeout=30)
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        
                # 使用锁保护共享变量
                if not hasattr(self, '_progress_lock'):
                    import threading
                    self._progress_lock = threading.Lock()
                    
                with self._progress_lock:
                    self.downloaded_count += 1
                    self.update_progress(self.downloaded_count, total)
                
                return True
            else:
                print(f"下载失败: {img['enddate']} - HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"下载失败: {img['enddate']} - {str(e)}")
            return False
            
    def update_progress(self, current, total):
        """更新进度条和状态"""
        self.progress['value'] = (current / total) * 100
        self.status_label.config(text=f"下载进度: {current}/{total} ({(current/total*100):.1f}%)")
        self.root.update()
        
    def start_download(self):
        """开始下载"""
        if not self.validate_inputs():
            return
            
        # 创建下载线程
        thread = threading.Thread(target=self.download_thread)
        thread.daemon = True
        thread.start()
        
    def run(self):
        """运行程序"""
        self.root.mainloop()

def main():
    # 设置DPI感知（Windows）
    if sys.platform == "win32":
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    
    root = tk.Tk()
    app = BingWallpaperDownloader(root)
    app.run()

if __name__ == "__main__":
    main()