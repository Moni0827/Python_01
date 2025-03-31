import os
import subprocess
import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sv_ttk  # 新增 Sun Valley TTK 主題支援

# 定義顏色主題
COLORS = {
    "light": {
        "bg": "#ffffff",
        "fg": "#000000",
        "button": "#0078D7",
        "button_fg": "#ffffff",
        "accent": "#0078D7",
    },
    "dark": {
        "bg": "#202020",
        "fg": "#ffffff",
        "button": "#404040",
        "button_fg": "#ffffff",
        "accent": "#0078D7",
    },
}

# 定義共用樣式
STYLES = {"padding": 10, "button_width": 15, "entry_width": 50}


def get_audio_duration(file_path):
    """獲取音訊檔案的長度"""
    try:
        # 使用 ffprobe 獲取媒體檔案資訊
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_format",
                "-show_streams",
                file_path,
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        # 解析 JSON 輸出
        data = json.loads(result.stdout)
        duration = float(data["format"]["duration"])

        # 將秒數轉換為時:分:秒格式
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    except Exception as e:
        print(f"無法獲取音訊長度: {str(e)}")
        return "未知"


def merge_audio_files(input_files, output_file):
    """合併多個音訊檔案"""
    # 創建一個包含所有輸入檔案的文字檔
    temp_list = "temp_file_list.txt"
    with open(temp_list, "w", encoding="utf-8") as f:
        for file in input_files:
            f.write(f"file '{file}'\n")

    try:
        # 使用 ffmpeg 的 concat 功能合併檔案
        subprocess.run(
            [
                "ffmpeg",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                temp_list,
                "-c",
                "copy",
                output_file,
            ],
            check=True,
        )
        print(f"成功合併音訊檔案到: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"合併失敗: {str(e)}")
    finally:
        # 刪除暫存的檔案列表
        if os.path.exists(temp_list):
            os.remove(temp_list)


def convert_mp4_to_mp3(input_file):
    """將MP4檔案轉換為MP3"""
    try:
        input_path = str(input_file).encode("utf-8").decode("utf-8")
        output_file = str(input_file).replace(".mp4", ".mp3")
        output_path = output_file.encode("utf-8").decode("utf-8")

        # 使用ffmpeg進行轉換
        subprocess.run(
            [
                "ffmpeg",
                "-i",
                input_path,
                "-vn",  # 不要視訊軌
                "-acodec",
                "libmp3lame",  # 使用MP3編碼器
                "-q:a",
                "2",  # 音質設定（0最好，9最差）
                output_path,
            ],
            check=True,
            encoding="utf-8",
            errors="replace",
        )
        print(f"成功轉換: {Path(input_path).name} -> {Path(output_path).name}")
    except UnicodeEncodeError as e:
        print(f"編碼錯誤: {str(e)}")
    except UnicodeDecodeError as e:
        print(f"解碼錯誤: {str(e)}")
    except subprocess.CalledProcessError as e:
        print(f"轉換失敗: {str(e)}")
    except Exception as e:
        print(f"未預期的錯誤: {str(e)}")


def trim_audio(input_file, output_file, start_time, end_time):
    """剪輯音訊檔案"""
    try:
        input_path = str(input_file).encode("utf-8").decode("utf-8")
        output_path = str(output_file).encode("utf-8").decode("utf-8")

        subprocess.run(
            [
                "ffmpeg",
                "-i",
                input_path,
                "-ss",
                start_time,  # 開始時間
                "-to",
                end_time,  # 結束時間
                "-c",
                "copy",  # 直接複製編碼，不重新編碼
                output_path,
            ],
            check=True,
            encoding="utf-8",
            errors="replace",
        )
        print(f"成功剪輯音訊: {Path(output_path).name}")
        return True
    except UnicodeEncodeError as e:
        print(f"編碼錯誤: {str(e)}")
        return False
    except UnicodeDecodeError as e:
        print(f"解碼錯誤: {str(e)}")
        return False
    except subprocess.CalledProcessError as e:
        print(f"剪輯失敗: {str(e)}")
        return False
    except Exception as e:
        print(f"未預期的錯誤: {str(e)}")
        return False


def format_time(seconds):
    """將秒數轉換為 HH:MM:SS 格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def parse_time(time_str):
    """將時間字串解析為秒數"""
    try:
        parts = time_str.split(":")
        if len(parts) == 2:
            minutes, seconds = parts
            return int(minutes) * 60 + int(seconds)
        elif len(parts) == 3:
            hours, minutes, seconds = parts
            return int(hours) * 3600 + int(minutes) * 60 + int(seconds)
        return 0
    except:
        return 0


class MP4ToMP3Converter(tk.Tk):
    def __init__(self):
        super().__init__()

        # 設定全域字體
        default_font = ("Microsoft JhengHei UI", 10)

        # 設定 ttk 風格
        style = ttk.Style()
        style.configure(".", font=default_font)

        # 初始化變數
        self.files_to_convert = []
        self.files_to_merge = []  # 新增合併檔案列表
        self.progress_var = tk.StringVar(value="")

        # 套用 Sun Valley 主題
        sv_ttk.set_theme("light")

        # 建立主要框架
        self.main_frame = ttk.Notebook(self)

        # 新增主題切換按鈕
        theme_button = ttk.Button(self, text="切換主題", command=self._toggle_theme)
        theme_button.pack(anchor="ne", padx=10, pady=5)

        self.title("音訊轉換與剪輯工具")
        self.geometry("800x600")

        # 設定主框架位置
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 轉換頁面
        self.convert_frame = ttk.Frame(self.main_frame, padding="10")
        self.main_frame.add(self.convert_frame, text="MP4轉MP3")

        # 合併頁面
        self.merge_frame = ttk.Frame(self.main_frame, padding="10")
        self.main_frame.add(self.merge_frame, text="音訊合併")

        # 剪輯頁面
        self.trim_frame = ttk.Frame(self.main_frame, padding="10")
        self.main_frame.add(self.trim_frame, text="音訊剪輯")

        # 分割頁面
        self.split_frame = ttk.Frame(self.main_frame, padding="10")
        self.main_frame.add(self.split_frame, text="音訊分割")

        # === 分割頁面元件 ===
        # 檔案選擇
        split_file_frame = ttk.Frame(self.split_frame)
        split_file_frame.pack(fill=tk.X, pady=5)

        self.split_file_var = tk.StringVar()
        ttk.Label(split_file_frame, text="選擇音訊檔案：").pack(side=tk.LEFT)
        ttk.Entry(split_file_frame, textvariable=self.split_file_var, width=50).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(split_file_frame, text="瀏覽", command=self.select_split_file).pack(
            side=tk.LEFT
        )

        # 分割時間
        split_time_frame = ttk.Frame(self.split_frame)
        split_time_frame.pack(fill=tk.X, pady=10)

        ttk.Label(split_time_frame, text="分割時間點 (HH:MM:SS 或 MM:SS)：").pack(
            side=tk.LEFT
        )
        self.split_time_var = tk.StringVar()
        ttk.Entry(split_time_frame, textvariable=self.split_time_var, width=10).pack(
            side=tk.LEFT, padx=5
        )

        # 分割按鈕
        ttk.Button(self.split_frame, text="開始分割", command=self.start_split).pack(
            pady=10
        )

        # === 剪輯頁面元件 ===
        # 檔案選擇
        trim_file_frame = ttk.Frame(self.trim_frame)
        trim_file_frame.pack(fill=tk.X, pady=5)

        self.trim_file_var = tk.StringVar()
        ttk.Label(trim_file_frame, text="選擇音訊檔案：").pack(side=tk.LEFT)
        ttk.Entry(trim_file_frame, textvariable=self.trim_file_var, width=50).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(trim_file_frame, text="瀏覽", command=self.select_trim_file).pack(
            side=tk.LEFT
        )

        # 時間選擇
        time_frame = ttk.Frame(self.trim_frame)
        time_frame.pack(fill=tk.X, pady=10)

        ttk.Label(time_frame, text="開始時間 (HH:MM:SS 或 MM:SS)：").pack(side=tk.LEFT)
        self.start_time_var = tk.StringVar()
        ttk.Entry(time_frame, textvariable=self.start_time_var, width=10).pack(
            side=tk.LEFT, padx=5
        )

        ttk.Label(time_frame, text="結束時間 (HH:MM:SS 或 MM:SS)：").pack(
            side=tk.LEFT, padx=5
        )
        self.end_time_var = tk.StringVar()
        ttk.Entry(time_frame, textvariable=self.end_time_var, width=10).pack(
            side=tk.LEFT
        )

        # 剪輯按鈕
        ttk.Button(self.trim_frame, text="開始剪輯", command=self.start_trim).pack(
            pady=10
        )

        # === 轉換頁面元件 ===
        # 檔案列表（使用 Treeview 替代 Listbox）
        columns = ("檔案名稱", "長度")
        self.file_list = ttk.Treeview(
            self.convert_frame, columns=columns, show="headings", height=15
        )
        self.file_list.heading("檔案名稱", text="檔案名稱")
        self.file_list.heading("長度", text="長度")
        self.file_list.column("長度", width=100, anchor="center")
        self.file_list.pack(pady=10, fill=tk.BOTH, expand=True)

        # 檔案列表框架（在轉換頁面中）
        button_frame = ttk.Frame(self.convert_frame)
        button_frame.pack(pady=5)

        ttk.Button(button_frame, text="選擇檔案", command=self.add_files).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="開始轉換", command=self.start_convert).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="清除列表", command=self.clear_list).pack(
            side=tk.LEFT, padx=5
        )

        # === 合併頁面元件 ===
        # 音訊檔案列表（使用 Treeview 替代 Listbox）
        merge_list_frame = ttk.Frame(self.merge_frame)
        merge_list_frame.pack(fill=tk.BOTH, expand=True)

        self.merge_list = ttk.Treeview(
            merge_list_frame, columns=columns, show="headings", height=15
        )
        self.merge_list.heading("檔案名稱", text="檔案名稱")
        self.merge_list.heading("長度", text="長度")
        self.merge_list.column("長度", width=100, anchor="center")
        self.merge_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 排序按鈕框架
        order_button_frame = ttk.Frame(merge_list_frame)
        order_button_frame.pack(side=tk.LEFT, padx=5)

        ttk.Button(order_button_frame, text="↑", command=self.move_up).pack(pady=2)
        ttk.Button(order_button_frame, text="↓", command=self.move_down).pack(pady=2)

        # 合併按鈕框架
        merge_button_frame = ttk.Frame(self.merge_frame)
        merge_button_frame.pack(pady=5)

        ttk.Button(
            merge_button_frame, text="選擇音訊檔案", command=self.add_audio_files
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(merge_button_frame, text="開始合併", command=self.start_merge).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(
            merge_button_frame, text="清除列表", command=self.clear_merge_list
        ).pack(side=tk.LEFT, padx=5)

        # 進度顯示
        ttk.Label(self, textvariable=self.progress_var).pack(pady=5)

    def _toggle_theme(self):
        """切換淺色/深色主題"""
        if sv_ttk.get_theme() == "dark":
            sv_ttk.set_theme("light")
        else:
            sv_ttk.set_theme("dark")

    def start_convert(self):
        """開始轉換所選檔案"""
        if not self.files_to_convert:
            messagebox.showwarning("警告", "請先選擇要轉換的MP4檔案")
            return

        try:
            self.progress_var.set("正在轉換檔案...")
            self.update()

            for file in self.files_to_convert:
                if os.path.exists(file):
                    convert_mp4_to_mp3(file)
                else:
                    messagebox.showerror("錯誤", f"找不到檔案：{file}")

            self.progress_var.set("轉換完成！")
            messagebox.showinfo("完成", "所有檔案已轉換完成！")
            self.clear_list()  # 清空檔案列表
        except Exception as e:
            self.progress_var.set("轉換過程發生錯誤！")
            messagebox.showerror("錯誤", f"轉換過程發生錯誤：{str(e)}")

    def add_files(self):
        files = filedialog.askopenfilenames(
            title="選擇MP4檔案",
            filetypes=[("MP4檔案", "*.mp4")],
            initialdir=os.path.dirname(os.path.abspath(__file__)),
        )
        for file in files:
            if file not in self.files_to_convert:
                self.files_to_convert.append(file)
                duration = get_audio_duration(file)
                self.file_list.insert(
                    "", tk.END, values=(os.path.basename(file), duration)
                )

    def add_audio_files(self):
        """選擇要合併的音訊檔案"""
        files = filedialog.askopenfilenames(
            title="選擇音訊檔案",
            filetypes=[("音訊檔案", "*.mp3 *.wav")],
            initialdir=os.path.dirname(os.path.abspath(__file__)),
        )
        for file in files:
            if file not in self.files_to_merge:
                self.files_to_merge.append(file)
                duration = get_audio_duration(file)
                self.merge_list.insert(
                    "", tk.END, values=(os.path.basename(file), duration)
                )

    def clear_list(self):
        self.file_list.delete(*self.file_list.get_children())
        self.files_to_convert.clear()

    def clear_merge_list(self):
        """清除合併列表"""
        self.merge_list.delete(*self.merge_list.get_children())
        self.files_to_merge.clear()

    def move_up(self):
        """將選中的檔案向上移動"""
        selection = self.merge_list.selection()
        if not selection:
            return

        item = selection[0]
        idx = self.merge_list.index(item)
        if idx == 0:
            return

        prev = self.merge_list.prev(item)
        if not prev:
            return

        # 獲取當前項目的值
        values = self.merge_list.item(item)["values"]
        prev_values = self.merge_list.item(prev)["values"]

        # 交換值
        self.merge_list.item(item, values=prev_values)
        self.merge_list.item(prev, values=values)

        # 更新選擇
        self.merge_list.selection_set(prev)

        # 更新檔案列表順序
        idx = self.merge_list.index(item)
        self.files_to_merge[idx], self.files_to_merge[idx - 1] = (
            self.files_to_merge[idx - 1],
            self.files_to_merge[idx],
        )

    def move_down(self):
        """將選中的檔案向下移動"""
        selection = self.merge_list.selection()
        if not selection:
            return

        item = selection[0]
        next_item = self.merge_list.next(item)
        if not next_item:
            return

        # 獲取當前項目的值
        values = self.merge_list.item(item)["values"]
        next_values = self.merge_list.item(next_item)["values"]

        # 交換值
        self.merge_list.item(item, values=next_values)
        self.merge_list.item(next_item, values=values)

        # 更新選擇
        self.merge_list.selection_set(next_item)

        # 更新檔案列表順序
        idx = self.merge_list.index(item)
        self.files_to_merge[idx], self.files_to_merge[idx + 1] = (
            self.files_to_merge[idx + 1],
            self.files_to_merge[idx],
        )

    def start_merge(self):
        """開始合併音訊檔案"""
        if len(self.files_to_merge) < 2:
            messagebox.showwarning("警告", "請至少選擇兩個音訊檔案進行合併")
            return

        output_file = filedialog.asksaveasfilename(
            title="儲存合併後的檔案",
            filetypes=[("MP3檔案", "*.mp3")],
            defaultextension=".mp3",
        )

        if output_file:
            self.progress_var.set("正在合併音訊檔案...")
            self.update()
            merge_audio_files(self.files_to_merge, output_file)
            self.progress_var.set("合併完成！")
            messagebox.showinfo("完成", "音訊檔案合併完成！")

    def select_trim_file(self):
        """選擇要剪輯的音訊檔案"""
        file = filedialog.askopenfilename(
            title="選擇音訊檔案",
            filetypes=[("音訊檔案", "*.mp3 *.wav")],
            initialdir=os.path.dirname(os.path.abspath(__file__)),
        )
        if file:
            self.trim_file_var.set(file)
            # 顯示音訊檔案的總長度
            duration = get_audio_duration(file)
            messagebox.showinfo("檔案資訊", f"音訊檔案長度：{duration}")

    def start_trim(self):
        """開始剪輯音訊"""
        input_file = self.trim_file_var.get()
        if not input_file or not os.path.exists(input_file):
            messagebox.showerror("錯誤", "請選擇有效的音訊檔案")
            return

        start_time = self.start_time_var.get()
        end_time = self.end_time_var.get()

        if not start_time or not end_time:
            messagebox.showerror("錯誤", "請輸入開始和結束時間")
            return

        # 選擇輸出檔案位置
        output_file = filedialog.asksaveasfilename(
            title="儲存剪輯後的檔案",
            filetypes=[("MP3檔案", "*.mp3"), ("WAV檔案", "*.wav")],
            defaultextension=".mp3",
        )

        if output_file:
            self.progress_var.set("正在剪輯音訊檔案...")
            self.update()

            if trim_audio(input_file, output_file, start_time, end_time):
                self.progress_var.set("剪輯完成！")
                messagebox.showinfo("完成", "音訊檔案剪輯完成！")
            else:
                self.progress_var.set("剪輯失敗！")
                messagebox.showerror("錯誤", "音訊剪輯過程中發生錯誤")

    def select_split_file(self):
        """選擇要分割的音訊檔案"""
        file = filedialog.askopenfilename(
            title="選擇音訊檔案",
            filetypes=[("音訊檔案", "*.mp3 *.wav")],
            initialdir=os.path.dirname(os.path.abspath(__file__)),
        )
        if file:
            self.split_file_var.set(file)
            # 顯示音訊檔案的總長度
            duration = get_audio_duration(file)
            messagebox.showinfo("檔案資訊", f"音訊檔案長度：{duration}")

    def start_split(self):
        """開始分割音訊"""
        input_file = self.split_file_var.get()
        if not input_file or not os.path.exists(input_file):
            messagebox.showerror("錯誤", "請選擇有效的音訊檔案")
            return

        split_time = self.split_time_var.get()
        if not split_time:
            messagebox.showerror("錯誤", "請輸入分割時間點")
            return

        self.progress_var.set("正在分割音訊檔案...")
        self.update()

        success, output_path1, output_path2 = split_audio(input_file, split_time)

        if success:
            self.progress_var.set("分割完成！")
            messagebox.showinfo(
                "完成",
                f"音訊檔案分割完成！\n第一部分：{os.path.basename(output_path1)}\n第二部分：{os.path.basename(output_path2)}",
            )
        else:
            self.progress_var.set("分割失敗！")
            messagebox.showerror("錯誤", "音訊分割過程中發生錯誤")


def split_audio(input_file, split_time):
    """在指定時間點分割音訊檔案"""
    try:
        input_path = str(input_file).encode("utf-8").decode("utf-8")
        file_name = os.path.splitext(os.path.basename(input_file))[0]
        file_ext = os.path.splitext(input_file)[1]
        output_path1 = os.path.join(
            os.path.dirname(input_file), f"{file_name}_part1{file_ext}"
        )
        output_path2 = os.path.join(
            os.path.dirname(input_file), f"{file_name}_part2{file_ext}"
        )

        # 分割第一部分
        subprocess.run(
            [
                "ffmpeg",
                "-i",
                input_path,
                "-t",
                split_time,  # 從開始到分割點
                "-acodec",
                "copy",
                output_path1,
            ],
            check=True,
            encoding="utf-8",
            errors="replace",
        )

        # 分割第二部分
        subprocess.run(
            [
                "ffmpeg",
                "-i",
                input_path,
                "-ss",
                split_time,  # 從分割點到結束
                "-acodec",
                "copy",
                output_path2,
            ],
            check=True,
            encoding="utf-8",
            errors="replace",
        )

        print(f"成功分割音訊: {Path(input_path).name}")
        return True, output_path1, output_path2
    except Exception as e:
        print(f"分割失敗: {str(e)}")
        return False, None, None


def main():
    app = MP4ToMP3Converter()
    app.mainloop()


if __name__ == "__main__":
    main()
