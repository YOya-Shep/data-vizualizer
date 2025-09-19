## Data Vizualizer

Приложение написанное на языке Python, позволяющее визуализировать данные, загруженные из файлов xlsx/xls/csv

Ниже виден основной интерфейс приложения
![Интерфейс приложения](https://github.com/YOya-Shep/data-vizualizer/blob/main/fotos/data_vizualizer.png)
Здесь можно выбрать входной файл и выходную папку перемещаясь в проводник, выбрать вид нужных графиков и изменить их настройки, приступить к 3 действиям (создание графиков, матрицы или анализ)


### Основные возможности приложения

+ Составление таблицы с основной информацией о данных с помощью кнопки "Анализ датасета". 

В таблице [dataset_asalysis](https://github.com/YOya-Shep/data-vizualizer/blob/main/results/dataset_analysis_20250919_014331.xlsx) для каждого столбца датасета будут найдены и записаны: тип данных (int64, float64, object...), число уникальных значений, число Non-Null, мода и выборка из случайных 5 значений, для числовых также рассчитаны минимум, максимум, среднее и медианное. 

+ Создание матрицы корреляции Пирсона и сохранение как файл с именем типа correlation_table_%Y%m%d_%H%M%S.xlsx. Пример таблицы приложен в [rezults](https://github.com/YOya-Shep/data-vizualizer/blob/main/results/correlation_table_20250919_014329.xlsx).
Матрица корреляции окрашивается по правилам таблицы ниже. В программном коде эти правила описаны в переменной `_CORRELATION_COLOR_MAP` класса `DataAnalyzer` файла `processor.py`.

| Интервал | HEX-код | Цвет |
|---------|---------|------|
| `== 1.0` | `FF0000` | <span style="display:inline-block;width:20px;height:20px;background:#FF0000;border:1px solid #ff0000ff; border-radius:2px;"></span> |
| `== -1.0` | `0000FF` | <span style="display:inline-block;width:20px;height:20px;background:#0000FF;border:1px solid #0000ffff; border-radius:2px;"></span> |
| `== 0.0` | `FFFFFF` | <span style="display:inline-block;width:20px;height:20px;background:#FFFFFF;border:1px solid #ffffffff; border-radius:2px;"></span> |
| `(0.8, 1.0]` | `FF4500` | <span style="display:inline-block;width:20px;height:20px;background:#FF4500;border:1px solid #ddd; border-radius:2px;"></span> |
| `(0.6, 0.8]` | `FF8C00` | <span style="display:inline-block;width:20px;height:20px;background:#FF8C00;border:1px solid #ddd; border-radius:2px;"></span> |
| `(0.4, 0.6]` | `FFFF00` | <span style="display:inline-block;width:20px;height:20px;background:#FFFF00;border:1px solid #ddd; border-radius:2px;"></span> |
| `(0.2, 0.4]` | `FFBC00` | <span style="display:inline-block;width:20px;height:20px;background:#FFBC00;border:1px solid #ddd; border-radius:2px;"></span> |
| `(0.0, 0.2]` | `FFFFE0` | <span style="display:inline-block;width:20px;height:20px;background:#FFFFE0;border:1px solid #ddd; border-radius:2px;"></span> |
| `[-0.2, 0.0)` | `BCFFFF` | <span style="display:inline-block;width:20px;height:20px;background:#BCFFFF;border:1px solid #ddd; border-radius:2px;"></span> |
| `[-0.4, -0.2)` | `00FFFF` | <span style="display:inline-block;width:20px;height:20px;background:#00FFFF;border:1px solid #ddd; border-radius:2px;"></span> |
| `[-0.6, -0.4)` | `25BEFF` | <span style="display:inline-block;width:20px;height:20px;background:#25BEFF;border:1px solid #ddd; border-radius:2px;"></span> |
| `[-0.8, -0.6)` | `0093D2` | <span style="display:inline-block;width:20px;height:20px;background:#0093D2;border:1px solid #ddd; border-radius:2px;"></span> |
| `[-1.0, -0.8)` | `0080FF` | <span style="display:inline-block;width:20px;height:20px;background:#0080FF;border:1px solid #ddd; border-radius:2px;"></span> |


+ Построение 3-x видов графиков. Можно выбрать построить 1 из типов или все одновременно, для этого нужно проставить галочки слева от нужных видов графиков.
    
    * scatter-plot

    Графики scatter-plot показывают зависимости между признаками. По умолчанию графики строятся для пар с корреляцией > 0,6. Пользователь может регулировать количество построенных графиков, изменяя условие отбора по значению модуля корреляции и выставляя значения от 0,00 до 1,00
    Пример для столбцов Session_Duration_(hours) и Calories_Burned с высокой положительной корреляцией = 0,91
    ![scatter-plot - Session_Duration_(hours)_vs_Calories_Burned](https://github.com/YOya-Shep/data-vizualizer/blob/main/results/Session_Duration_(hours)_vs_Calories_Burned.png)
    Пример для столбцов Age и Weight_(kg) с низкой отрицательной корреляцией = -0,04
    ![scatter-plot - Age_vs_Weight_(kg)](https://github.com/YOya-Shep/data-vizualizer/blob/main/results/Age_vs_Weight_(kg).png)
    Пример для столбцов Calories_Burned и Fat_Percentage со средней отрицательной корреляцией = -0,60
    ![scatter-plot - Calories_Burned_vs_Fat_Percentage](https://github.com/YOya-Shep/data-vizualizer/blob/main/results/Calories_Burned_vs_Fat_Percentage.png)
    Пример для столбцов Calories_Burned и Workout_Frequency_(days_week) с средней положительной корреляцией = 0,58. Этот график отличает от остальных по виду, из-за того что Workout_Frequency_(days_week) содержит информацию о количестве тренировок в неделю, это целые числа int64.
    ![scatter-plot - Calories_Burned_vs_Workout_Frequency_(days_week)](https://github.com/YOya-Shep/data-vizualizer/blob/main/results/Calories_Burned_vs_Workout_Frequency_(days_week).png)

    * pie

    Строит простые круговые диаграммы для категориальных признаков. 
    Пример для Workout_Type типа object
    ![pie - Workout Type](https://github.com/YOya-Shep/data-vizualizer/blob/main/results/Workout_Type.png)
    Пример для Experience_Level типа измененного на category
    ![pie - Experience Level](https://github.com/YOya-Shep/data-vizualizer/blob/main/results/Experience_Level.png)

    * histogram

    Строит гистограммы числовых столбцов с разделением по категориям, и столбчатые диаграммы с разделением одних категориальных признаков по другим категориальным признакам. По умолчанию bins=15, но пользователь может выставить другое значение в диапазоне [1; 50]
    Пример для числового столбца Calories_Burned разделенного по Gender, bins=50
    ![histogram - Calories_Burned_by_Gender](https://github.com/YOya-Shep/data-vizualizer/blob/main/results/Calories_Burned_by_Gender.png)
    Пример для числового столбца Height_(m) разделенного по Gender, bins=15
    ![histogram - Height_(m)_by_Gender](https://github.com/YOya-Shep/data-vizualizer/blob/main/results/Height_(m)_by_Gender.png)
    Пример для object-столбца Workout_Type разделенного по Experience_Level, 4 варианта Workout_Type и 3 варианта Experience_Level
    ![bar - Workout_Type_by_Experience_Level](https://github.com/YOya-Shep/data-vizualizer/blob/main/results/Workout_Type_by_Experience_Level.png)
    Пример для числового столбца Session_Duration_(hours) разделенного по Experience_Level, bins=50
    ![histogram - Session_Duration_(hours)_by_Experience_Level](https://github.com/YOya-Shep/data-vizualizer/blob/main/results/Session_Duration_(hours)_by_Experience_Level.png)


### обработка ошибок и всплывающие окна


В случае если пользователь не выберет входной файл, выходную папку и нажмет накнопки выполнения действия, программа покажет соответствующее предупреждение и сообщит пользователю о том, что необходимо ещё сделать для успешного запуска. Также программа проверяет подходит ли содержимое входного файла, существует ли выбранный файл или выбранная выходная папка. Когда пользователь строит графики, программа проверяет, чтобы хотя бы возле одного вида графиков стояла галочка.
![error_no_file](https://github.com/YOya-Shep/data-vizualizer/blob/main/fotos/error_no_file.png)

Если пользователь нажмет кнопку выполнения какого-либо действия, ему высветится диалоговое окно с возможностью прекратить выполнение программы. Таким образом, пользователь сможет отменить действие, изменить параметры при необходимости или запустить выполнение другого действия.
![implementation](https://github.com/YOya-Shep/data-vizualizer/blob/main/fotos/implementation.png)

При успешной отмене пользователю высветится простое диалогове окно
![stop](https://github.com/YOya-Shep/data-vizualizer/blob/main/fotos/stop.png)

При завершении работы, программа выводит стандартное сообщение об успехе
![success](https://github.com/YOya-Shep/data-vizualizer/blob/main/fotos/success.png)

В качестве улучшения разработанного приложения можно:
+ добавить логгирование для записи выполняемых действий и возможных ошибок
+ добавить больше разнообразия при построении графиков (например scatter-plot с разными радиусами)

### немного о наборе данных

Приложение было протестированно на данных о [посетителях тренажерного зала](https://www.kaggle.com/datasets/valakhorasani/gym-members-exercise-dataset/data "перейти к gym-members-exercise-dataset"). За публикацию на kaggle открытого набора данных подходящего для тестирования благодарю [vala khorasani](https://www.kaggle.com/valakhorasani)

Для того чтобы удобнее проматривать данные я использую Rainbow CSV в Visual Studio Code
![rainbow_csv](https://github.com/YOya-Shep/data-vizualizer/blob/main/fotos/rainbow_csv.png)

В связи с особенностями набора данных в `processor.py` была добавлена специальная функция `convert_int_columns_to_categorical`. Она автоматически преобразует значения [1, 2, 3] в : "Beginner", "Medium", "Expert". Это было нужно для столбца Experience_Level, тк ранговые переменные подходят по смыслу больше, чем считываемые числовые. Функция работает на любых столбцах, содержащих только значения [1, 2, 3].
Подробнее о информацию датасете (измененном) можно посмотреть в [результатах]( "dataset_asalysis")

### код

Код приложения состоит из 3-х py файлов
+ main.py - для запуска
+ interface.py - для описания интерфейса, основных ошибок и всплывающих окон
+ processor.py - для описания функционала приложения, функций для построения графиков и таблиц

Здесь были использованы следующие версии библиотек:
```
matplotlib==3.10.6
openpyxl==3.1.5
pandas==2.3.2
```
Поскольку основной функционал приложения достаточно базовый и простой, то можно заменить и на более старые версии библиотек.

Также для реализации интерфейса были импортированы:
```
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
```

И для основного функционала использованы:
```
import os
from contextlib import contextmanager
from datetime import datetime
from typing import List, Optional

import matplotlib.pyplot as plt
import openpyxl
import pandas as pd
```


Код проверен линтерами isort и ruff. Ruff сейчас показывает, что некоторые `except Exception as e:` необходимо изменить, но это происходит из-за того, что выводы print в настоящий момент закомментированы. Приложение собрано в исполняемый `.exe` файл с помощью `pyinstaller`. Скачать DataVizualizer_v1 можно [здесь]()
