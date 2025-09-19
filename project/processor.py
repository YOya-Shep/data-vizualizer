import os
from contextlib import contextmanager
from datetime import datetime
from typing import List, Optional

import matplotlib.pyplot as plt
import openpyxl
import pandas as pd


class DataAnalyzer:
    
    _CORRELATION_COLOR_MAP = {
        # Точечные значения
        ("point", 1.0, None): "FF0000",
        ("point", -1.0, None): "0000FF",
        ("point", 0.0, None): "FFFFFF",

        # Положительная часть (с, а]
        ("left_parenthesis_right_bracket", 0.8, 1.0): "FF4500",
        ("left_parenthesis_right_bracket", 0.6, 0.8): "FF8C00",
        ("left_parenthesis_right_bracket", 0.4, 0.6): "FFFF00",
        ("left_parenthesis_right_bracket", 0.2, 0.4): "FFBC00",
           ("left_parenthesis_right_bracket", 0.0, 0.2): "FFFFE0",

        # Отрицательная часть [-а, -с)
        ("left_bracket_right_parenthesis", -0.2, 0.0): "BCFFFF",
        ("left_bracket_right_parenthesis", -0.4, -0.2): "00FFFF",
        ("left_bracket_right_parenthesis", -0.6, -0.4): "25BEFF",
        ("left_bracket_right_parenthesis", -0.8, -0.6): "0093D2",
        ("left_bracket_right_parenthesis", -1.0, -0.8): "0080FF", 
    }

    def __init__(self):
        self.data: Optional[pd.DataFrame] = None
        self.is_canceled: bool = False


    def load_file(self, file_path: str) -> bool:
        
        try:
            if file_path.lower().endswith('.csv'):
                self.data = pd.read_csv(file_path)
            elif file_path.lower().endswith(('.xlsx', '.xls')):
                self.data = pd.read_excel(file_path)
            else:
                raise ValueError("Неподдерживаемый формат файла.")
            # print(f"Данные успешно загружены: {file_path}")
            
            self.convert_int_columns_to_categorical()

            return True
        
        except Exception as e:
            # print(f"Ошибка загрузки файла: {e}")
            return False

    def get_numeric_columns(self)-> List[str]:
        if self.data is None:
            return []
        return self.data.select_dtypes(include=['int64', 'float64']).columns.tolist()

    def get_categorical_columns(self)-> List[str]:
        if self.data is None:
            return []
        return self.data.select_dtypes(include=['object', 'category']).columns.tolist()
    
    def convert_int_columns_to_categorical(self):
        """
        Автоматически преобразует значения [1, 2, 3] в категориальные: "Beginner", "Medium", "Expert". Нужно для столбца Experience_Level
        """
        if self.data is None:
            return

        numeric_cols = self.get_numeric_columns()

        for col in numeric_cols:

            if not pd.api.types.is_integer_dtype(self.data[col]):
                continue

            unique_vals = sorted(self.data[col].dropna().unique())

            if set(unique_vals) == {1, 2, 3} and len(unique_vals) == 3:
                mapping = { 
                    1: "Beginner", 
                    2: "Medium", 
                    3: "Expert" 
                    }
                self.data[col] = pd.Categorical(self.data[col].map(mapping),
                                                categories=["Beginner", "Medium", "Expert"], ordered=True )
        

    # Заменяет недопустимые символы для файловых имён
    @staticmethod
    def sanitize_filename(name: str) -> str:
        invalid_chars = '<>:;"|!?*\\/ \t\n\r'
        sanitized = ""
        for char in name:
            if char in invalid_chars:
                sanitized += "_"
            else:
                sanitized += char

        while "__" in sanitized:
            sanitized = sanitized.replace("__", "_")
        
        sanitized = sanitized.strip("_")

        if not sanitized:
            sanitized = "unknown"

        return sanitized

    def build_correlation_matrix(self, output_folder: str) -> bool:
        if self.data is None:
            return False

        numeric_cols = self.get_numeric_columns()
        if len(numeric_cols) < 2:
            return False

        corr_matrix = self.data[numeric_cols].corr()

        color_map = DataAnalyzer._CORRELATION_COLOR_MAP

        def get_correlation_color(r):

            for key, hex_color in color_map.items():
                key_type, min_val, max_val = key

                if key_type == "point": # точки 1, 0, -1
                    if r == min_val:
                        return hex_color

                elif key_type == "left_parenthesis_right_bracket":  # (min, max]
                    if min_val < r <= max_val:
                        return hex_color

                elif key_type == "left_bracket_right_parenthesis":  # [min, max)
                    if min_val <= r < max_val:
                        return hex_color

            return "000000"  # не должно случиться

        colors_grid = []
        for row in corr_matrix.values:
            row_colors = []
            for val in row:
                hex_color = get_correlation_color(val)
                row_colors.append(hex_color)
            colors_grid.append(row_colors)

        output_path = os.path.join(output_folder, f"correlation_table_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            corr_matrix.to_excel(writer, sheet_name='Корреляция')

            worksheet = writer.sheets['Корреляция']

            for row_idx, row_colors in enumerate(colors_grid):
                for col_idx, hex_color in enumerate(row_colors):
                    cell_row = row_idx + 2  
                    cell_col = col_idx + 2
                    fill = openpyxl.styles.PatternFill(
                        start_color=hex_color,
                        end_color=hex_color,
                        fill_type="solid"
                    )
                    worksheet.cell(row=cell_row, column=cell_col).fill = fill   

        return True
 

    def build_scatter_charts(self, output_folder: str, threshold: float = 0.6) -> bool:

        if self.data is None:
            return False

        numeric_cols = self.get_numeric_columns()
        if len(numeric_cols) < 2:
            return False

        corr_matrix = self.data[numeric_cols].corr()
        scatter_dir = os.path.join(output_folder, f"scatter_plot_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        os.makedirs(scatter_dir, exist_ok=True)


        try:
            with self.check_cancel():
                
                for i in range(len(numeric_cols)):
                    for j in range(i + 1, len(numeric_cols)):                        
                        if abs(corr_matrix.iloc[i, j]) >= threshold:  # модуль корреляции
                            x_col, y_col = numeric_cols[i], numeric_cols[j]
                            plt.figure(figsize=(8, 6))
                            plt.scatter(self.data[x_col], self.data[y_col], alpha=0.6, color='blue')
                            plt.title(f'Scatter Plot: {x_col} vs {y_col} (cor={corr_matrix.iloc[i, j]:.2f})')
                            plt.xlabel(x_col)
                            plt.ylabel(y_col)
                            plt.grid(True, linestyle='--', alpha=0.7)
                            save_path = os.path.join(scatter_dir, f"{self.sanitize_filename(x_col)}_vs_{self.sanitize_filename(y_col)}.png")
                            plt.savefig(save_path, dpi=150, bbox_inches='tight')
                            plt.close()
       
        except KeyboardInterrupt:
            # print("Процесс прерван пользователем.")
            return False
        except Exception as e:
            # print(f"Ошибка при построении scatter_plot: {e}")
            return False
        
        return True

    def build_pie_charts(self, output_folder: str) -> bool:

        if self.data is None:
            return False

        cat_cols = self.get_categorical_columns()
        pie_dir = os.path.join(output_folder, f"pie_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        os.makedirs(pie_dir, exist_ok=True)
        
        try:
            with self.check_cancel():
                for col in self.guarded_iter(cat_cols, "Круговые диаграммы прерваны"):
                    counts = self.data[col].value_counts()
                    plt.figure(figsize=(8, 6))
                    plt.pie(counts.values, labels=counts.index, autopct='%1.1f%%', startangle=90)
                    plt.title(f'Распределение: {col}')
                    save_path = os.path.join(pie_dir, f"{self.sanitize_filename(col)}.png")
                    plt.savefig(save_path, dpi=150, bbox_inches='tight')
                    plt.close()

        except KeyboardInterrupt:
            # print("Процесс прерван пользователем.")
            return False
        except Exception as e:
            # print(f"Ошибка при построении круговых диаграмм: {e}")
            return False

        return True
    
    def build_histogram_charts(self, output_folder: str, bins: int = 15) -> bool:
        
        if self.data is None:
            return False

        numeric_cols = self.get_numeric_columns()
        cat_cols = self.get_categorical_columns()

        # Если нет категориальных столбцов для разбиения, то гистограммы не будут построены
        if not cat_cols:
            return False

        hist_dir = os.path.join(output_folder, f"histogram_by_category_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        os.makedirs(hist_dir, exist_ok=True)

        colors = plt.cm.Set1.colors
        
        try:
            with self.check_cancel():
        
                # Гистограммы числовых столбцов разделенные по категориальным
                for num_col in self.guarded_iter(numeric_cols, "Гистограммы прерваны"):
                    for group_col in self.guarded_iter(cat_cols, "Гистограммы прерваны"):
                
                        plt.figure(figsize=(10, 6))
                        categories = self.data[group_col].dropna().unique()

                        for i, cat_val in enumerate(categories):
                            subset = self.data[(self.data[group_col] == cat_val) & (self.data[num_col].notna())][num_col]
                            if len(subset) == 0:
                                continue
                            plt.hist(
                                subset,
                                alpha=0.7,
                                label=str(cat_val),
                                color=colors[i % len(colors)],
                                edgecolor='black',
                                bins=bins
                            )

                        plt.xlabel(num_col)
                        plt.ylabel('Частота')
                        plt.title(f'Распределение {num_col} по {group_col}')
                        plt.legend(title=group_col, bbox_to_anchor=(1.05, 1), loc='upper left')
                        plt.grid(True, linestyle='--', alpha=0.6)
                        plt.tight_layout()

                        safe_num = self.sanitize_filename(num_col)
                        safe_group = self.sanitize_filename(group_col)
                        save_path = os.path.join(hist_dir, f"{safe_num}_by_{safe_group}.png")
                        plt.savefig(save_path, dpi=150, bbox_inches='tight')
                        plt.close()
                        # print(f" Сохранена гистограмма: {save_path}")

                # Столбчатые диаграммы: распределение одной категориальной переменной по другой
                for target_col in self.guarded_iter(cat_cols, "Диаграммы прерваны"):
                    for group_col in self.guarded_iter(cat_cols, "Диаграммы прерваны"):
                        if target_col == group_col:
                            continue

                        cross_tab = pd.crosstab(self.data[target_col], self.data[group_col])
                        cross_tab_normalized = cross_tab.div(cross_tab.sum(axis=1), axis=0)

                        x = range(len(cross_tab.index))
                        width = 0.8 / len(cross_tab.columns)

                        plt.figure(figsize=(10, 6))

                        for i, group_val in enumerate(cross_tab.columns):
                            values = cross_tab_normalized[group_val].values
                            positions = [x_i + i * width for x_i in x]
                            plt.bar(positions, values, width=width, label=str(group_val),
                                    color=colors[i % len(colors)], edgecolor='black', alpha=0.7)

                        plt.xticks([x_i + width * (len(cross_tab.columns)-1)/2 for x_i in x], cross_tab.index, rotation=45, ha='right')
                        plt.ylabel('Доля')
                        plt.title(f'Распределение {target_col} по {group_col}')
                        plt.legend(title=group_col, bbox_to_anchor=(1.05, 1), loc='upper left')
                        plt.grid(axis='y', linestyle='--', alpha=0.6)
                        plt.tight_layout()

                        safe_target = self.sanitize_filename(target_col)
                        safe_group = self.sanitize_filename(group_col)
                        save_path = os.path.join(hist_dir, f"{safe_target}_by_{safe_group}.png")
                        plt.savefig(save_path, dpi=150, bbox_inches='tight')
                        plt.close()
                        # print(f" Сохранена столбчатая диаграмма: {save_path}")

        except KeyboardInterrupt:
            # print("Процесс прерван пользователем.")
            return False
        except Exception as e:
            # print(f"Ошибка при построении гистограмм: {e}")
            return False
        
        return True
    

    def analyze_dataset(self, output_folder: str) -> bool:
        if self.data is None:
            return False

        df = self.data.copy()
        df.columns = df.columns.astype(str)

        COLUMNS = [
            'Column', 'Type', 'Unique Values', 'Non-Null',
            'Min', 'Max', 'Mean', 'Median', 'Mode', 'Examples'
        ]

        summary = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            values = df[col].dropna()
            unique_count = len(values.unique())
            non_null = len(values)

            row = {col_name: "N/A" for col_name in COLUMNS}
            row.update({
                'Column': col,
                'Type': dtype,
                'Unique Values': unique_count,
                'Non-Null': non_null,
            })

            if pd.api.types.is_numeric_dtype(df[col]):
                row.update({
                    'Min': values.min(),
                    'Max': values.max(),
                    'Mean': round(values.mean(), 4),
                    'Median': round(values.median(), 4),
                    'Mode': values.mode().iloc[0] if len(values.mode()) > 0 else "N/A",
                    'Examples': str(values.sample(n=5, random_state=None).tolist())
                })
            else:
                row.update({
                    'Mode': values.value_counts().idxmax() if not values.empty else "N/A",
                    'Examples': str(values.unique().tolist())
                })

            summary.append(row)

        path = os.path.join(output_folder, f"dataset_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")

        with pd.ExcelWriter(path, engine='openpyxl') as writer:
            pd.DataFrame(summary, columns=COLUMNS).to_excel(writer, sheet_name='Info', index=False)

        return True


    @contextmanager
    def check_cancel(self):
        try:
            yield
        except Exception:
            if self.is_canceled:
                raise KeyboardInterrupt("Отмена пользователем") from None
            else:
                raise

    def guarded_iter(self, iterable, msg="Процесс прерван"):
        for item in iterable:
            if self.is_canceled:
                # print(f"{msg}")
                raise StopIteration()
            yield item

    # Сбрасывает флаг отмены перед новым запуском
    def reset(self) -> None:
        self.is_canceled = False
    
    # Устанавливает флаг отмены
    def cancel(self) -> None:
        self.is_canceled = True
