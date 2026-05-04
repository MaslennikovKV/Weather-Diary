import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
from pathlib import Path

class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary - Дневник погоды")
        self.root.geometry("950x650")
        
        self.weather_records = []
        self.filename = "weather_data.json"
        
        self.load_data()
        self.create_widgets()
        self.refresh_table()
    
    def create_widgets(self):
        # Фрейм для ввода данных
        input_frame = tk.LabelFrame(self.root, text="Добавить запись о погоде", 
                                   padx=10, pady=10, font=("Arial", 10, "bold"))
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Дата
        tk.Label(input_frame, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=0, sticky="w", pady=5)
        self.date_entry = tk.Entry(input_frame, width=15, font=("Arial", 10))
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))
        
        # Температура
        tk.Label(input_frame, text="Температура (°C):").grid(row=0, column=2, sticky="w", pady=5)
        self.temperature_entry = tk.Entry(input_frame, width=10, font=("Arial", 10))
        self.temperature_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Описание погоды
        tk.Label(input_frame, text="Описание:").grid(row=0, column=4, sticky="w", pady=5)
        self.description_entry = tk.Entry(input_frame, width=25, font=("Arial", 10))
        self.description_entry.grid(row=0, column=5, padx=5, pady=5)
        
        # Осадки
        tk.Label(input_frame, text="Осадки:").grid(row=0, column=6, sticky="w", pady=5)
        self.precipitation_var = tk.StringVar(value="нет")
        precipitation_frame = tk.Frame(input_frame)
        precipitation_frame.grid(row=0, column=7, padx=5, pady=5)
        
        self.precipitation_yes = tk.Radiobutton(precipitation_frame, text="Да", 
                                                 variable=self.precipitation_var, 
                                                 value="да")
        self.precipitation_yes.pack(side="left")
        
        self.precipitation_no = tk.Radiobutton(precipitation_frame, text="Нет", 
                                                variable=self.precipitation_var, 
                                                value="нет")
        self.precipitation_no.pack(side="left")
        
        # Кнопка добавления
        self.add_button = tk.Button(input_frame, text="Добавить запись", 
                                    command=self.add_record, bg="#4CAF50", fg="white",
                                    font=("Arial", 10, "bold"), padx=20)
        self.add_button.grid(row=0, column=8, padx=20, pady=5)
        
        # Фрейм для фильтрации
        filter_frame = tk.LabelFrame(self.root, text="Фильтрация записей", 
                                    padx=10, pady=10, font=("Arial", 10, "bold"))
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        # Фильтр по дате
        tk.Label(filter_frame, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=0, sticky="w", pady=5)
        self.filter_date_entry = tk.Entry(filter_frame, width=15, font=("Arial", 10))
        self.filter_date_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Фильтр по температуре
        tk.Label(filter_frame, text="Температура от (°C):").grid(row=0, column=2, sticky="w", pady=5)
        self.filter_temp_entry = tk.Entry(filter_frame, width=10, font=("Arial", 10))
        self.filter_temp_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Фильтр по осадкам
        tk.Label(filter_frame, text="Осадки:").grid(row=0, column=4, sticky="w", pady=5)
        self.filter_precipitation_var = tk.StringVar(value="все")
        filter_precipitation_combo = ttk.Combobox(filter_frame, 
                                                  textvariable=self.filter_precipitation_var,
                                                  values=["все", "да", "нет"], 
                                                  width=8, font=("Arial", 10))
        filter_precipitation_combo.grid(row=0, column=5, padx=5, pady=5)
        
        # Кнопки фильтрации
        self.apply_filter_button = tk.Button(filter_frame, text="Применить фильтр", 
                                             command=self.refresh_table, bg="#2196F3", 
                                             fg="white", font=("Arial", 10, "bold"))
        self.apply_filter_button.grid(row=0, column=6, padx=10, pady=5)
        
        self.reset_filter_button = tk.Button(filter_frame, text="Сбросить фильтры", 
                                            command=self.reset_filter, bg="#FF5722", 
                                            fg="white", font=("Arial", 10, "bold"))
        self.reset_filter_button.grid(row=0, column=7, padx=10, pady=5)
        
        # Таблица записей
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Создание таблицы
        columns = ("id", "date", "temperature", "description", "precipitation")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Заголовки таблицы
        self.tree.heading("id", text="№")
        self.tree.heading("date", text="Дата")
        self.tree.heading("temperature", text="Температура (°C)")
        self.tree.heading("description", text="Описание погоды")
        self.tree.heading("precipitation", text="Осадки")
        
        # Ширина колонок
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("date", width=120, anchor="center")
        self.tree.column("temperature", width=130, anchor="center")
        self.tree.column("description", width=300)
        self.tree.column("precipitation", width=100, anchor="center")
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Кнопки управления записями
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        self.delete_button = tk.Button(button_frame, text="Удалить запись", 
                                       command=self.delete_record, bg="#f44336", 
                                       fg="white", font=("Arial", 10))
        self.delete_button.pack(side="left", padx=5)
        
        self.edit_button = tk.Button(button_frame, text="Редактировать запись", 
                                     command=self.edit_record, bg="#FF9800", 
                                     fg="white", font=("Arial", 10))
        self.edit_button.pack(side="left", padx=5)
        
        self.clear_button = tk.Button(button_frame, text="Очистить поля", 
                                      command=self.clear_inputs, bg="#9E9E9E", 
                                      fg="white", font=("Arial", 10))
        self.clear_button.pack(side="left", padx=5)
        
        # Статистика
        stats_frame = tk.Frame(self.root)
        stats_frame.pack(fill="x", padx=10, pady=5)
        
        self.stats_label = tk.Label(stats_frame, text="", 
                                    font=("Arial", 11, "bold"), fg="#333333")
        self.stats_label.pack()
        
        # Привязка двойного клика для редактирования
        self.tree.bind("<Double-1>", self.on_double_click)
        
        # Переменная для отслеживания редактирования
        self.editing_id = None
    
    def validate_date(self, date_str):
        """Проверка корректности даты"""
        try:
            datetime.strptime(date_str, "%d.%m.%Y")
            return True
        except (ValueError, TypeError):
            return False
    
    def validate_temperature(self, temp_str):
        """Проверка корректности температуры"""
        try:
            float(temp_str)
            return True
        except (ValueError, TypeError):
            return False
    
    def validate_description(self, description):
        """Проверка описания"""
        return bool(description and description.strip())
    
    def add_record(self):
        """Добавление новой записи о погоде"""
        date = self.date_entry.get().strip()
        temperature = self.temperature_entry.get().strip()
        description = self.description_entry.get().strip()
        precipitation = self.precipitation_var.get()
        
        # Валидация данных
        if not date or not temperature or not description:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return
        
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Дата должна быть в формате ДД.ММ.ГГГГ!")
            return
        
        if not self.validate_temperature(temperature):
            messagebox.showerror("Ошибка", "Температура должна быть числом!")
            return
        
        if not self.validate_description(description):
            messagebox.showerror("Ошибка", "Описание погоды не может быть пустым!")
            return
        
        # Создание записи
        record = {
            "id": self.get_next_id(),
            "date": date,
            "temperature": float(temperature),
            "description": description,
            "precipitation": precipitation
        }
        
        self.weather_records.append(record)
        self.save_data()
        self.refresh_table()
        self.clear_inputs()
        
        messagebox.showinfo("Успех", "Запись о погоде добавлена!")
    
    def edit_record(self):
        """Редактирование выбранной записи"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для редактирования!")
            return
        
        self.on_double_click(None)
    
    def on_double_click(self, event):
        """Обработчик двойного клика для редактирования"""
        selected = self.tree.selection()
        if not selected:
            return
        
        # Получаем данные выбранной строки
        item = self.tree.item(selected[0])
        values = item['values']
        
        # Находим запись в списке
        for record in self.weather_records:
            if record["id"] == int(values[0]):
                # Заполняем поля для редактирования
                self.editing_id = record["id"]
                
                self.date_entry.delete(0, tk.END)
                self.date_entry.insert(0, record["date"])
                
                self.temperature_entry.delete(0, tk.END)
                self.temperature_entry.insert(0, record["temperature"])
                
                self.description_entry.delete(0, tk.END)
                self.description_entry.insert(0, record["description"])
                
                self.precipitation_var.set(record["precipitation"])
                
                # Меняем текст кнопки
                self.add_button.config(text="Сохранить изменения", bg="#FF9800")
                break
    
    def save_edited_record(self):
        """Сохранение отредактированной записи"""
        if self.editing_id is None:
            return
        
        date = self.date_entry.get().strip()
        temperature = self.temperature_entry.get().strip()
        description = self.description_entry.get().strip()
        precipitation = self.precipitation_var.get()
        
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
        
        if not self.validate_description(description):
            messagebox.showerror("Ошибка", "Описание погоды не может быть пустым!")
            return
        
        # Обновление записи
        for record in self.weather_records:
            if record["id"] == self.editing_id:
                record["date"] = date
                record["temperature"] = float(temperature)
                record["description"] = description
                record["precipitation"] = precipitation
                break
        
        self.save_data()
        self.refresh_table()
        self.clear_inputs()
        self.cancel_editing()
        
        messagebox.showinfo("Успех", "Запись обновлена!")
    
    def cancel_editing(self):
        """Отмена режима редактирования"""
        self.editing_id = None
        self.add_button.config(text="Добавить запись", bg="#4CAF50")
    
    def add_or_update(self):
        """Определение действия: добавление или обновление"""
        if self.editing_id is not None:
            self.save_edited_record()
        else:
            self.add_record()
    
    def delete_record(self):
        """Удаление выбранной записи"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления!")
            return
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить запись?"):
            item = self.tree.item(selected[0])
            record_id = int(item['values'][0])
            
            # Удаляем запись
            self.weather_records = [r for r in self.weather_records if r["id"] != record_id]
            
            self.save_data()
            self.refresh_table()
            self.cancel_editing()
            
            messagebox.showinfo("Успех", "Запись удалена!")
    
    def get_next_id(self):
        """Генерация уникального ID"""
        if self.weather_records:
            return max(record["id"] for record in self.weather_records) + 1
        return 1
    
    def get_filtered_records(self):
        """Получение отфильтрованных записей"""
        filtered = self.weather_records.copy()
        
        # Фильтр по дате
        filter_date = self.filter_date_entry.get().strip()
        if filter_date:
            if not self.validate_date(filter_date):
                messagebox.showerror("Ошибка", "Неверный формат даты в фильтре!")
                return None
            filtered = [r for r in filtered if r["date"] == filter_date]
        
        # Фильтр по температуре
        filter_temp = self.filter_temp_entry.get().strip()
        if filter_temp:
            if not self.validate_temperature(filter_temp):
                messagebox.showerror("Ошибка", "Температура в фильтре должна быть числом!")
                return None
            min_temp = float(filter_temp)
            filtered = [r for r in filtered if r["temperature"] >= min_temp]
        
        # Фильтр по осадкам
        filter_precipitation = self.filter_precipitation_var.get()
        if filter_precipitation != "все":
            filtered = [r for r in filtered if r["precipitation"] == filter_precipitation]
        
        return filtered
    
    def refresh_table(self):
        """Обновление таблицы и статистики"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Получение отфильтрованных данных
        filtered_records = self.get_filtered_records()
        if filtered_records is None:
            return
        
        # Заполнение таблицы
        for record in filtered_records:
            self.tree.insert("", "end", values=(
                record["id"],
                record["date"],
                f"{record['temperature']:.1f}",
                record["description"],
                record["precipitation"]
            ))
        
        # Обновление статистики
        self.update_statistics(filtered_records)
    
    def update_statistics(self, records):
        """Обновление статистической информации"""
        if not records:
            self.stats_label.config(text="Нет записей для отображения")
            return
        
        total_records = len(records)
        temperatures = [r["temperature"] for r in records]
        avg_temp = sum(temperatures) / len(temperatures)
        max_temp = max(temperatures)
        min_temp = min(temperatures)
        
        precipitation_count = len([r for r in records if r["precipitation"] == "да"])
        
        stats_text = f"Записей: {total_records} | "
        stats_text += f"Средняя температура: {avg_temp:.1f}°C | "
        stats_text += f"Макс: {max_temp:.1f}°C | "
        stats_text += f"Мин: {min_temp:.1f}°C | "
        stats_text += f"Дней с осадками: {precipitation_count}"
        
        self.stats_label.config(text=stats_text)
    
    def reset_filter(self):
        """Сброс фильтров"""
        self.filter_date_entry.delete(0, tk.END)
        self.filter_temp_entry.delete(0, tk.END)
        self.filter_precipitation_var.set("все")
        self.refresh_table()
    
    def clear_inputs(self):
        """Очистка полей ввода"""
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))
        self.temperature_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.precipitation_var.set("нет")
    
    def save_data(self):
        """Сохранение данных в JSON файл"""
        try:
            data_path = Path(self.filename)
            with open(data_path, 'w', encoding='utf-8') as f:
                json.dump(self.weather_records, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")
    
    def load_data(self):
        """Загрузка данных из JSON файла"""
        data_path = Path(self.filename)
        if data_path.exists():
            try:
                with open(data_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content.strip():
                        self.weather_records = json.loads(content)
                    else:
                        self.weather_records = []
            except json.JSONDecodeError:
                messagebox.showerror("Ошибка", "Файл данных поврежден. Создаем новый.")
                self.weather_records = []
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
                self.weather_records = []
        else:
            self.weather_records = []

def main():
    root = tk.Tk()
    app = WeatherDiary(root)
    
    # Привязка кнопки к методу add_or_update
    app.add_button.config(command=app.add_or_update)
    
    root.mainloop()

if __name__ == "__main__":
    main()