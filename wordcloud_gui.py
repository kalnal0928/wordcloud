import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from konlpy.tag import Okt
import re
from collections import Counter
import pandas as pd
import threading
from PIL import Image, ImageTk
import io

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

class WordCloudGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("워드클라우드 생성기")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        self.wordcloud_result = None
        self.word_counts = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 좌측 패널 (입력 및 설정)
        left_frame = ttk.LabelFrame(main_frame, text="텍스트 입력 및 설정", padding="10")
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # 파일 선택 섹션
        file_frame = ttk.Frame(left_frame)
        file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(file_frame, text="파일 선택:").grid(row=0, column=0, sticky=tk.W)
        self.file_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path_var, width=40).grid(row=1, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(file_frame, text="찾아보기", command=self.browse_file).grid(row=1, column=1)
        ttk.Button(file_frame, text="파일 읽기", command=self.load_file).grid(row=1, column=2, padx=(5, 0))
        
        # 텍스트 입력 섹션
        ttk.Label(left_frame, text="텍스트 직접 입력:").grid(row=1, column=0, sticky=tk.W, pady=(10, 5))
        self.text_input = scrolledtext.ScrolledText(left_frame, width=50, height=15, wrap=tk.WORD)
        self.text_input.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 설정 섹션
        settings_frame = ttk.LabelFrame(left_frame, text="워드클라우드 설정", padding="5")
        settings_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 최대 단어 수
        ttk.Label(settings_frame, text="최대 단어 수:").grid(row=0, column=0, sticky=tk.W)
        self.max_words = tk.IntVar(value=100)
        ttk.Spinbox(settings_frame, from_=50, to=500, textvariable=self.max_words, width=10).grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        # 최소 단어 길이
        ttk.Label(settings_frame, text="최소 단어 길이:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.min_word_length = tk.IntVar(value=2)
        ttk.Spinbox(settings_frame, from_=1, to=5, textvariable=self.min_word_length, width=10).grid(row=1, column=1, sticky=tk.W, padx=(5, 0))
        
        # 색상 테마
        ttk.Label(settings_frame, text="색상 테마:").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        self.color_scheme = tk.StringVar(value="Set3")
        color_combo = ttk.Combobox(settings_frame, textvariable=self.color_scheme, values=["Set3", "viridis", "plasma", "inferno", "magma", "coolwarm"], width=12)
        color_combo.grid(row=2, column=1, sticky=tk.W, padx=(5, 0))
        
        # 생성 버튼
        ttk.Button(left_frame, text="워드클라우드 생성", command=self.generate_wordcloud, style='Accent.TButton').grid(row=4, column=0, pady=10)
        
        # 진행률 표시
        self.progress = ttk.Progressbar(left_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 상태 표시
        self.status_var = tk.StringVar(value="준비됨")
        ttk.Label(left_frame, textvariable=self.status_var).grid(row=6, column=0, sticky=tk.W)
        
        # 우측 패널 (결과 표시)
        right_frame = ttk.LabelFrame(main_frame, text="결과", padding="10")
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        # 탭 생성
        notebook = ttk.Notebook(right_frame)
        notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 워드클라우드 탭
        self.wordcloud_frame = ttk.Frame(notebook)
        notebook.add(self.wordcloud_frame, text="워드클라우드")
        
        # 단어 빈도 탭
        self.frequency_frame = ttk.Frame(notebook)
        notebook.add(self.frequency_frame, text="단어 빈도")
        
        # 단어 빈도 표시용 트리뷰
        columns = ('순위', '단어', '빈도')
        self.frequency_tree = ttk.Treeview(self.frequency_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.frequency_tree.heading(col, text=col)
            self.frequency_tree.column(col, width=100)
        
        # 스크롤바 추가
        scrollbar = ttk.Scrollbar(self.frequency_frame, orient=tk.VERTICAL, command=self.frequency_tree.yview)
        self.frequency_tree.configure(yscrollcommand=scrollbar.set)
        
        self.frequency_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 저장 버튼
        save_frame = ttk.Frame(right_frame)
        save_frame.grid(row=1, column=0, pady=(10, 0))
        
        ttk.Button(save_frame, text="워드클라우드 저장", command=self.save_wordcloud).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(save_frame, text="단어빈도 저장", command=self.save_frequency).grid(row=0, column=1)
        
        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(0, weight=1)
        left_frame.rowconfigure(2, weight=1)
        right_frame.rowconfigure(0, weight=1)
        self.frequency_frame.rowconfigure(0, weight=1)
        self.frequency_frame.columnconfigure(0, weight=1)
        file_frame.columnconfigure(0, weight=1)
        
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="텍스트 파일 선택",
            filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")]
        )
        if filename:
            self.file_path_var.set(filename)
    
    def load_file(self):
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showwarning("경고", "파일을 선택해주세요.")
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            self.text_input.delete(1.0, tk.END)
            self.text_input.insert(1.0, text)
            self.status_var.set(f"파일 로드 완료: {len(text)}자")
            
        except Exception as e:
            messagebox.showerror("오류", f"파일을 읽는 중 오류가 발생했습니다:\n{str(e)}")
    
    def generate_wordcloud(self):
        text = self.text_input.get(1.0, tk.END).strip()
        if not text:
            messagebox.showwarning("경고", "텍스트를 입력해주세요.")
            return
        
        # 진행률 표시 시작
        self.progress.start()
        self.status_var.set("워드클라우드 생성 중...")
        
        # 별도 스레드에서 실행
        thread = threading.Thread(target=self._generate_wordcloud_thread, args=(text,))
        thread.daemon = True
        thread.start()
    
    def _generate_wordcloud_thread(self, text):
        try:
            # 한국어 형태소 분석
            okt = Okt()
            clean_text = re.sub(r'[^가-힣\s]', '', text)
            words = okt.nouns(clean_text)
            
            # 필터링
            stop_words = ['의', '가', '이', '은', '는', '을', '를', '에', '와', '과', '한', '하다', '있다', '되다', '그', '저', '것', '수', '들', '지', '고', '되다', '다', '로', '으로', '에서', '에게', '한테', '께서']
            min_length = self.min_word_length.get()
            good_words = [word for word in words if len(word) >= min_length and word not in stop_words]
            
            if not good_words:
                self.root.after(0, self._show_no_words_warning)
                return
            
            # 단어 빈도수 계산
            self.word_counts = Counter(good_words)
            
            # 워드클라우드 생성
            self.wordcloud_result = WordCloud(
                font_path='malgun.ttf',
                width=800,
                height=600,
                background_color='white',
                max_words=self.max_words.get(),
                colormap=self.color_scheme.get()
            ).generate_from_frequencies(self.word_counts)
            
            # UI 업데이트는 메인 스레드에서
            self.root.after(0, self._update_ui)
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda msg=error_msg: self._show_error(msg))
            self.root.after(0, self._stop_progress)
    
    def _show_error(self, error_msg):
        messagebox.showerror("오류", f"워드클라우드 생성 중 오류가 발생했습니다:\n{error_msg}")
    
    def _show_no_words_warning(self):
        messagebox.showwarning("경고", "분석할 수 있는 단어가 없습니다.")
        self.progress.stop()
    
    def _stop_progress(self):
        self.progress.stop()
    
    def _update_ui(self):
        # 진행률 표시 중지
        self.progress.stop()
        self.status_var.set("워드클라우드 생성 완료")
        
        # 워드클라우드 표시
        self._display_wordcloud()
        
        # 단어 빈도 표시
        self._display_frequency()
    
    def _display_wordcloud(self):
        # 기존 위젯 제거
        for widget in self.wordcloud_frame.winfo_children():
            widget.destroy()
        
        # matplotlib figure 생성
        fig, ax = plt.subplots(figsize=(10, 7))
        ax.imshow(self.wordcloud_result, interpolation='bilinear')
        ax.axis('off')
        ax.set_title('워드클라우드', fontsize=16, pad=20)
        
        # tkinter에 표시
        canvas = FigureCanvasTkAgg(fig, self.wordcloud_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _display_frequency(self):
        # 기존 데이터 제거
        for item in self.frequency_tree.get_children():
            self.frequency_tree.delete(item)
        
        # 상위 50개 단어만 표시
        for i, (word, count) in enumerate(self.word_counts.most_common(50), 1):
            self.frequency_tree.insert('', 'end', values=(i, word, count))
    
    def save_wordcloud(self):
        if self.wordcloud_result is None:
            messagebox.showwarning("경고", "먼저 워드클라우드를 생성해주세요.")
            return
        
        filename = filedialog.asksaveasfilename(
            title="워드클라우드 저장",
            defaultextension=".png",
            filetypes=[("PNG 파일", "*.png"), ("JPEG 파일", "*.jpg"), ("모든 파일", "*.*")]
        )
        
        if filename:
            try:
                self.wordcloud_result.to_file(filename)
                messagebox.showinfo("성공", f"워드클라우드가 저장되었습니다:\n{filename}")
            except Exception as e:
                messagebox.showerror("오류", f"저장 중 오류가 발생했습니다:\n{str(e)}")
    
    def save_frequency(self):
        if self.word_counts is None:
            messagebox.showwarning("경고", "먼저 워드클라우드를 생성해주세요.")
            return
        
        filename = filedialog.asksaveasfilename(
            title="단어 빈도 저장",
            defaultextension=".csv",
            filetypes=[("CSV 파일", "*.csv"), ("엑셀 파일", "*.xlsx"), ("모든 파일", "*.*")]
        )
        
        if filename:
            try:
                df = pd.DataFrame(self.word_counts.items(), columns=['단어', '빈도수'])
                df = df.sort_values(by="빈도수", ascending=False).reset_index(drop=True)
                
                if filename.endswith('.xlsx'):
                    df.to_excel(filename, index=False)
                else:
                    df.to_csv(filename, index=False, encoding='utf-8-sig')
                
                messagebox.showinfo("성공", f"단어 빈도가 저장되었습니다:\n{filename}")
            except Exception as e:
                messagebox.showerror("오류", f"저장 중 오류가 발생했습니다:\n{str(e)}")

def main():
    root = tk.Tk()
    app = WordCloudGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()