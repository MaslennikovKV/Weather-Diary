import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os

class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary")
        self.root.geometry("800x600")
        
        self.records = []
        self.filename = "weather_data.json"
        
        self.load_data()
        self.create_widgets()
        self.refresh_table()
    
    def create_widgets(self):
        # Фрейм для ввода данных
        input_frame = tk.LabelFrame(self.root, text="Добавить запись", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Дата
        tk.Label(input_frame, text="Дата:").grid(row=0, column=0, sticky="w")
        self.date_entry = tk.Entry(input_frame, width=12)
        self.date_entry.grid(row=0, column=1, padx=5)
        self.date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))
        
        # Температура
        tk.Label(input_frame, text="Температура (°C):").grid(row=0, column=2, sticky="w")
        self.temp_entry = tk.Entry(input_frame, width=10)
        self.temp_entry.grid(row=0, column=3, padx=5)
        
        # Описание погоды
        tk.Label(input_frame, text="Описание:").grid(row=0, column=4, sticky="w")
        self.desc_entry = tk.Entry(input_frame, width=20)
        self.desc_entry.grid(row=0, column=5, padx=5)
        
        # Осадки
        tk.Label(input_frame, text="Осадки:").grid(row=0, column=6, sticky="w")
        self.precip_var = tk.StringVar(value="нет")
        precip_combo = ttk.Combobox(input_frame, textvariable=self.precip_var, 
                                     values=["да", "нет"], width=5)
        precip_combo.grid(row=0, column=7, padx=5)
        
        # Кнопка добавления
        self.add_button = tk.Button(input_frame, text="Добавить запись", 
                                    command=self.add_record, bg="#4CAF50", fg="white")
        self.add_button.grid(row=0, column=8, padx=20)
        
        # Фрейм для фильтрации
        filter_frame = tk.LabelFrame(self.root, text="Фильтрация", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        # Фильтр по дате
        tk.Label(filter_frame, text="Дата:").grid(row=0, column=0, sticky="w")
        self.filter_date_entry = tk.Entry(filter_frame, width=12)
        self.filter_date_entry.grid(row=0, column=1, padx=5)
        
        # Фильтр по температуре
        tk.Label(filter_frame, text="Температура от (°C):").grid(row=0, column=2, sticky="w")
        self.filter_temp_entry = tk.Entry(filter_frame, width=10)
        self.filter_temp_entry.grid(row=0, column=3, padx=5)
        
        # Кнопка фильтрации
        self.filter_button = tk.Button(filter_frame, text="Применить фильтр", 
                                       command=self.refresh_table, bg="#2196F3", fg="white")
        self.filter_button.grid(row=0, column=4, padx=20)
        
        # Кнопка сброса фильтра
        self.reset_button = tk.Button(filter_frame, text="Сбросить", 
                                      command=self.reset_filter, bg="#FF5722", fg="white")
        self.reset_button.grid(row=0, column=5, padx=5)
        
        # Таблица записей
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        columns = ("id", "date", "temperature", "description", "precipitation")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        self.tree.heading("id", text="№")
        self.tree.heading("date", text="Дата")
        self.tree.heading("temperature", text="Температура")
        self.tree.heading("description", text="Описание")
        self.tree.heading("precipitation", text="Осадки")
        
        self.tree.column("id", width=50)
        self.tree.column("date", width=100)
        self.tree.column("temperature", width=100)
        self.tree.column("description", width=250)
        self.tree.column("precipitation", width=70)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%d.%m.%Y")
            return True
        except ValueError:
            return False
    
    def validate_temperature(self, temp_str):
        try:
            float(temp_str)
            return True
        except ValueError:
            return False
    
    def add_record(self):
        date = self.date_entry.get().strip()
        temperature = self.temp_entry.get().strip()
        description = self.desc_entry.get().strip()
        precipitation = self.precip_var.get()
        
        # Валидация
        if not date or not temperature or not description:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return
        
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Дата должна быть в формате ДД.ММ.ГГГГ!")
            return
        
        if not self.validate_temperature(temperature):
            messagebox.showerror("Ошибка", "Температура должна быть числом!")
            return
        
        # Добавление записи
        record = {
            "id": len(self.records) + 1,
            "date": date,
            "temperature": float(temperature),
            "description": description,
            "precipitation": precipitation
        }
        
        self.records.append(record)
        self.save_data()
        self.refresh_table()
        
        # Очистка полей
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))
        
        messagebox.showinfo("Успех", "Запись добавлена!")
    
    def get_filtered_records(self):
        filtered = self.records.copy()
        
        # Фильтр по дате
        filter_date = self.filter_date_entry.get().strip()
        if filter_date:
            if not self.validate_date(filter_date):
                messagebox.showerror("Ошибка", "Неверный формат даты!")
                return None
            filtered = [r for r in filtered if r["date"] == filter_date]
        
        # Фильтр по температуре
        filter_temp = self.filter_temp_entry.get().strip()
        if filter_temp:
            if not self.validate_temperature(filter_temp):
                messagebox.showerror("Ошибка", "Температура должна быть числом!")
                return None
            min_temp = float(filter_temp)
            filtered = [r for r in filtered if r["temperature"] >= min_temp]
        
        return filtered
    
    def refresh_table(self):
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Получение отфильтрованных данных
        filtered_records = self.get_filtered_records()
        if filtered_records is None:
            return
        
        # Заполнение таблицы
        for i, record in enumerate(filtered_records, 1):
            self.tree.insert("", "end", values=(
                i, 
                record['date'], 
                record['temperature'],
                record['description'], 
                record['precipitation']
            ))
    
    def reset_filter(self):
        self.filter_date_entry.delete(0, tk.END)
        self.filter_temp_entry.delete(0, tk.END)
        self.refresh_table()
    
    def save_data(self):
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.records, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")
    
    def load_data(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    self.records = json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
                self.records = []

def main():
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()

if __name__ == "__main__":
    main()
