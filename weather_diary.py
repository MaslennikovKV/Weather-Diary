import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

DATA_FILE = "weather_data.json"

class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Дневник погоды")
        self.root.geometry("750x550")

        # Список записей (каждая — словарь)
        self.records = []

        # --- Фрейм ввода ---
        input_frame = ttk.LabelFrame(root, text="Новая запись", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="w", pady=2)
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=1, sticky="w", padx=5)
        # Пример плейсхолдера
        self.date_entry.insert(0, "2026-05-04")

        ttk.Label(input_frame, text="Температура (°C):").grid(row=1, column=0, sticky="w", pady=2)
        self.temp_entry = ttk.Entry(input_frame, width=10)
        self.temp_entry.grid(row=1, column=1, sticky="w", padx=5)
        self.temp_entry.insert(0, "20")

        ttk.Label(input_frame, text="Описание:").grid(row=2, column=0, sticky="w", pady=2)
        self.desc_entry = ttk.Entry(input_frame, width=40)
        self.desc_entry.grid(row=2, column=1, columnspan=2, sticky="w", padx=5)
        self.desc_entry.insert(0, "Солнечно")

        self.precip_var = tk.BooleanVar()
        ttk.Checkbutton(input_frame, text="Осадки", variable=self.precip_var).grid(row=3, column=1, sticky="w", pady=2)

        ttk.Button(input_frame, text="Добавить запись", command=self.add_record).grid(row=4, column=0, columnspan=3, pady=10)

        # --- Таблица для отображения ---
        table_frame = ttk.Frame(root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("date", "temp", "desc", "precip")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        self.tree.heading("date", text="Дата")
        self.tree.heading("temp", text="Температура")
        self.tree.heading("desc", text="Описание")
        self.tree.heading("precip", text="Осадки")
        self.tree.column("date", width=100)
        self.tree.column("temp", width=100)
        self.tree.column("desc", width=300)
        self.tree.column("precip", width=80)
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # --- Панель фильтрации ---
        filter_frame = ttk.LabelFrame(root, text="Фильтры", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Дата:").grid(row=0, column=0, padx=5, sticky="w")
        self.filter_date = ttk.Entry(filter_frame, width=12)
        self.filter_date.grid(row=0, column=1, padx=5, sticky="w")

        ttk.Label(filter_frame, text="Температура >=").grid(row=0, column=2, padx=5, sticky="w")
        self.filter_temp = ttk.Entry(filter_frame, width=8)
        self.filter_temp.grid(row=0, column=3, padx=5, sticky="w")

        ttk.Button(filter_frame, text="Применить", command=self.apply_filters).grid(row=0, column=4, padx=10)
        ttk.Button(filter_frame, text="Сбросить", command=self.reset_filters).grid(row=0, column=5, padx=5)

        # --- Кнопки сохранения/загрузки ---
        io_frame = ttk.Frame(root)
        io_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(io_frame, text="Сохранить в JSON", command=self.save_to_json).pack(side="left", padx=5)
        ttk.Button(io_frame, text="Загрузить из JSON", command=self.load_from_json).pack(side="left", padx=5)
        ttk.Button(io_frame, text="Очистить таблицу", command=self.clear_table).pack(side="left", padx=5)

        # Загружаем данные при старте, если файл существует
        if os.path.exists(DATA_FILE):
            self.load_from_json()

    # ------------------ Валидация ------------------
    def validate_input(self, date_str, temp_str, desc_str):
        errors = []
        # Проверка даты
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            errors.append("Дата должна быть в формате ГГГГ-ММ-ДД (например, 2026-05-04).")
        # Проверка температуры
        try:
            float(temp_str)
        except ValueError:
            errors.append("Температура должна быть числом.")
        # Проверка описания
        if not desc_str.strip():
            errors.append("Описание не может быть пустым.")
        return errors

    # ------------------ Добавление записи ------------------
    def add_record(self):
        date = self.date_entry.get().strip()
        temp = self.temp_entry.get().strip()
        desc = self.desc_entry.get().strip()
        precip = self.precip_var.get()

        errors = self.validate_input(date, temp, desc)
        if errors:
            messagebox.showerror("Ошибка ввода", "\n".join(errors))
            return

        record = {
            "date": date,
            "temperature": float(temp),
            "description": desc,
            "precipitation": precip
        }
        self.records.append(record)
        self.update_table(self.records)
        # Очистка полей (опционально)
        self.date_entry.delete(0, tk.END)
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precip_var.set(False)

    # ------------------ Обновление таблицы ------------------
    def update_table(self, records_to_show):
        # Очистка
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Заполнение
        for rec in records_to_show:
            precip_text = "Да" if rec["precipitation"] else "Нет"
            self.tree.insert("", tk.END, values=(
                rec["date"],
                rec["temperature"],
                rec["description"],
                precip_text
            ))

    # ------------------ Фильтрация ------------------
    def apply_filters(self):
        filtered = self.records[:]

        # Фильтр по дате
        filter_date = self.filter_date.get().strip()
        if filter_date:
            filtered = [r for r in filtered if r["date"] == filter_date]

        # Фильтр по температуре
        filter_temp = self.filter_temp.get().strip()
        if filter_temp:
            try:
                min_temp = float(filter_temp)
                filtered = [r for r in filtered if r["temperature"] >= min_temp]
            except ValueError:
                messagebox.showerror("Ошибка фильтра", "Введите числовое значение температуры.")
                return

        self.update_table(filtered)

    def reset_filters(self):
        self.filter_date.delete(0, tk.END)
        self.filter_temp.delete(0, tk.END)
        self.update_table(self.records)

    # ------------------ Сохранение и загрузка ------------------
    def save_to_json(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.records, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Успех", f"Данные сохранены в {DATA_FILE}")
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", str(e))

    def load_from_json(self):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.records = json.load(f)
            self.update_table(self.records)
            # Не показываем сообщение при автоматической загрузке при старте
            if hasattr(self, '_manual_load'):
                messagebox.showinfo("Успех", "Данные загружены.")
        except FileNotFoundError:
            pass
        except Exception as e:
            messagebox.showerror("Ошибка загрузки", str(e))

    def clear_table(self):
        self.tree.delete(*self.tree.get_children())

# ---------- Точка входа ----------
if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()
