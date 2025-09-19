import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox


class GUInterface:
    def __init__(self, processor):
        
        self.processor = processor
        self.root = tk.Tk()
        self.root.title("Data Vizualizer")
        self.root.geometry("700x600") # ширина*высота
        self.root.resizable(True, True)
        self.common_font = ('Helvetica', 10, 'bold')

        self.xlsx_path = tk.StringVar()
        self.output_folder = tk.StringVar()

        self.graph_types = {
            "scatter": tk.BooleanVar(value=False),
            "pie": tk.BooleanVar(value=False),
            "histogram": tk.BooleanVar(value=False),
        }

        self.scatter_threshold = tk.DoubleVar(value=0.6)
        self.histogram_bins = tk.IntVar(value=15)

        # Потоки
        self.processing_window = None
        self.thread = None

        self.create_widgets()


    def create_widgets(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(expand=True)

        tk.Label(main_frame, text="Это приложение нужно, чтобы \n " \
        "строить различные графики или таблицу корреляции на основе входных данных",
                 font=self.common_font, justify='center').pack(pady=(0, 20))

        # Выбор входного файла
        tk.Label(main_frame, text="Выберите входной файл (.xlsx, .xls, .csv):",
                 font=self.common_font).pack(anchor='center', pady=(10, 5))
        tk.Entry(main_frame, textvariable=self.xlsx_path, state='readonly',
                 width=60, font=self.common_font, justify='center').pack(pady=5)
        tk.Button(main_frame, text="Выбрать...", command=self.browse_input_file,
                  bg='#c5a9db', font=self.common_font, width=25).pack(pady=5)

        # Выбор выходной папки
        tk.Label(main_frame, text="Выбранная выходная папка:",
                 font=self.common_font).pack(anchor='center', pady=(20, 5))
        tk.Entry(main_frame, textvariable=self.output_folder, state='readonly',
                 width=60, font=self.common_font, justify='center').pack(pady=5)
        tk.Button(main_frame, text="Выбрать выходную папку",
                  command=self.browse_output_folder, bg='#c5a9db',
                  font=self.common_font, width=25).pack(pady=5)
        

        # Выбор типов графиков и их настроек
        tk.Label(main_frame, text="Выберите типы графиков:", 
                 font=self.common_font).pack(anchor='w', pady=(30, 10))

        graph_frame = tk.Frame(main_frame)
        graph_frame.pack(fill='x', pady=10)

        tk.Checkbutton(graph_frame, text="Scatter plot (с отбором по модулю корреляции)", 
                       variable=self.graph_types["scatter"], 
                       font=self.common_font).grid(row=1, column=0, sticky='w', padx=5, pady=5)
        tk.Label(graph_frame, text="|cor| >", font=self.common_font).grid(row=1, column=1, sticky='w')
        tk.Scale(graph_frame, from_=0.0, to=1.0, resolution=0.01, variable=self.scatter_threshold, 
                        orient='horizontal', length=150).grid(row=1, column=2)

        tk.Checkbutton(graph_frame, text="Круговые диаграммы", 
                       variable=self.graph_types["pie"], 
                       font=self.common_font).grid(row=2, column=0, sticky='w', padx=5, pady=5)

        tk.Checkbutton(graph_frame, text="Гистограммы (с разделением по категориям)", 
                       variable=self.graph_types["histogram"], 
                       font=self.common_font).grid(row=3, column=0, sticky='w', padx=5, pady=5)
        tk.Label(graph_frame, text="bins =", font=self.common_font).grid(row=3, column=1, sticky='w')
        tk.Scale(graph_frame, from_=1, to=50, variable=self.histogram_bins, 
                        orient='horizontal', length=150).grid(row=3, column=2)

        # Кнопки действий
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=20)
        button_height = 2

        tk.Button(button_frame, text="Построить графики",
                  command=self.build_graphs, bg='#8cc98b',
                  font=self.common_font, width=20, height=button_height).pack(side='left', padx=10)       
        
        tk.Button(button_frame, text="Построить матрицу корреляции",
                  command=self.build_correlation, bg='#8cc98b',
                  font=self.common_font, width=30, height=button_height).pack(side='left', padx=10)
        
        tk.Button(button_frame, text="Анализ датасета",
                command=self.analyze_dataset, bg='#8cc98b',
                font=self.common_font, width=20, height=button_height).pack(side='left', padx=10)


    # Выбор входного файла
    def browse_input_file(self):
        file_path = filedialog.askopenfilename(
            title="Выберите файл",
            filetypes=[
                ("Excel files", "*.xlsx *.xls"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.xlsx_path.set(file_path)

    def browse_output_folder(self):
        folder_path = filedialog.askdirectory(title="Выберите папку для сохранения")
        if folder_path:
            self.output_folder.set(folder_path)


    # Диалоговые окна и обработка ошибок
    
    def show_processing_dialog(self, message):
        dialog = tk.Toplevel(self.root)
        dialog.title("Процесс выполнения")
        dialog.geometry("450x150")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)

        tk.Label(dialog, text=message, wraplength=400, font=self.common_font).pack(pady=20)
        tk.Button(dialog, text="СТОП", command=lambda: self.cancel_process(dialog),
                  bg='#bd7b7b', font=self.common_font, width=12).pack(pady=10)

        self.processing_window = dialog

    def cancel_process(self, dialog):
        if self.thread and self.thread.is_alive():
            self.processor.cancel()
            dialog.destroy()
            messagebox.showinfo("Отмена", "Процесс был отменён пользователем.")
        else:
            dialog.destroy()

    def _show_error_on_main_thread(self, message):
        self.root.after(0, lambda msg=message: messagebox.showerror("Ошибка", msg))

    def _show_info_on_main_thread(self, message):
        self.root.after(0, lambda msg=message: messagebox.showinfo("Успех", msg))

    def _show_warning_on_main_thread(self, message):
        self.root.after(0, lambda msg=message: messagebox.showwarning("Предупреждение", msg))

    def _validate_inputs(self):

        if not self.xlsx_path.get():
            self._show_warning_on_main_thread("Не выбран входной файл!")
            return False

        if not os.path.exists(self.xlsx_path.get()):
            self._show_error_on_main_thread("Файл не найден!")
            return False

        if not self.output_folder.get():
            self._show_warning_on_main_thread("Не выбрана выходная папка!")
            return False

        return True    

    def _close_processing_dialog(self):
        if self.processing_window:
            self.processing_window.destroy()
            self.processing_window = None


    # Выполнение действий button

    def build_correlation(self):
        if not self._validate_inputs():
            return
        self.thread = threading.Thread(target=self._build_correlation_thread)
        self.thread.start()
        
    def _build_correlation_thread(self):
        try:

            self.processor.reset()

            self.show_processing_dialog("Построение матрицы корреляции...")

            if not self.processor.load_file(self.xlsx_path.get()):
                self._show_error_on_main_thread("Не удалось загрузить данные.")
                return

            if self.processor.data.empty:
                self._show_error_on_main_thread("Таблица пустая или некорректная.")
                return

            success = self.processor.build_correlation_matrix(self.output_folder.get())
            if success:
                self._show_info_on_main_thread(f"Матрица корреляции сохранена в:\n{self.output_folder.get()}")
            else:
                self._show_error_on_main_thread("Не удалось построить матрицу корреляции.")
        except Exception as e:
            self._show_error_on_main_thread(f"Произошла ошибка: {e}")
        finally:
            self._close_processing_dialog()


    def build_graphs(self):
        selected = sum(self.graph_types[typ].get() for typ in self.graph_types)
        if selected == 0:
            self._show_warning_on_main_thread("Не выбран ни один тип графика!")
            return

        if not self._validate_inputs():
            return

        self.thread = threading.Thread(target=self._build_graphs_thread)
        self.thread.start()

    def _build_graphs_thread(self):   
        try:

            self.processor.reset()

            graph_list = []
            for name, var in self.graph_types.items():
                if var.get():
                    if name == "scatter":
                        graph_list.append("scatter-графики")
                    elif name == "pie":
                        graph_list.append("круговые диаграммы")
                    elif name == "histogram":
                        graph_list.append("гистограммы")
                    else:
                        graph_list.append("bliat gde i")
            msg = f"Построение графиков: {', '.join(graph_list)}..."
            self.show_processing_dialog(msg)

            if not self.processor.load_file(self.xlsx_path.get()):
                self._show_error_on_main_thread("Не удалось загрузить данные.")
                return

            if self.processor.data.empty:
                self._show_error_on_main_thread("Таблица пустая или некорректная.")
                return

            results = {}

            for name, var in self.graph_types.items():
                if var.get():
                    method = getattr(self.processor, f"build_{name}_charts")
                    if name == "scatter":
                        results[name] = method(self.output_folder.get(), threshold=self.scatter_threshold.get())
                    elif name == "pie":
                        results[name] = method(self.output_folder.get())
                    elif name == "histogram":
                        results[name] = method(self.output_folder.get(), bins=self.histogram_bins.get())
                    else:
                        results[name] = method(self.output_folder.get())  # Отработает eсли будут другие без параметров. Можно заменить на pass или на вызов ошибки. Сейчас сюда нельзя попасть
            
            # отмена
            if all(not success for success in results.values()):
                return
            success_count = sum(results.values())
            
            if success_count > 0:
                self._show_info_on_main_thread(f"Графики успешно построены и сохранены в:\n{self.output_folder.get()}")
            else:
                self._show_error_on_main_thread("Не удалось построить ни одного графика.")
        
        except Exception as e:
            self._show_error_on_main_thread(f"Произошла ошибка: {e}") 
        finally:
            self._close_processing_dialog()


    def analyze_dataset(self):
        if not self._validate_inputs():
            return

        self.thread = threading.Thread(target=self._analyze_dataset_thread)
        self.thread.start()

    def _analyze_dataset_thread(self):
        try:

            self.processor.reset()
            self.show_processing_dialog("Анализ датасета...")

            if not self.processor.load_file(self.xlsx_path.get()):
                self._show_error_on_main_thread("Не удалось загрузить данные.")
                return

            success = self.processor.analyze_dataset(self.output_folder.get())

            if success:
                self._show_info_on_main_thread(f"Анализ датасета сохранён:\n{self.output_folder.get()}")
            else:
                self._show_error_on_main_thread("Не удалось проанализировать датасет.")

        except Exception as e:
            self._show_error_on_main_thread(f"Произошла ошибка: {e}")
        finally:
            self._close_processing_dialog()

    # Запуск
    def run(self):
        self.root.mainloop()
