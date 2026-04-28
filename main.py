import json
import os
from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime

# Имя файла для хранения данных
DATA_FILE = "weather_data.json"

class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Дневник погоды")
        self.root.geometry("750x500")

        # Загружаем данные из JSON
        self.records = self.load_data()

        # Создаём интерфейс
        self.create_input_frame()
        self.create_filter_frame()
        self.create_table()

        # Отображаем все записи
        self.refresh_table()

    # ------------------- ЗАГРУЗКА / СОХРАНЕНИЕ -------------------
    def load_data(self):
        """Загружает записи из JSON файла"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_data(self):
        """Сохраняет записи в JSON файл"""
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.records, f, ensure_ascii=False, indent=4)

    # ------------------- ВАЛИДАЦИЯ -------------------
    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except:
            return False

    def validate_temperature(self, temp_str):
        try:
            float(temp_str)
            return True
        except:
            return False

    # ------------------- ДОБАВЛЕНИЕ -------------------
    def add_record(self):
        date = self.entry_date.get()
        temp = self.entry_temp.get()
        desc = self.entry_desc.get()
        precip = self.precip_var.get()

        # Проверки
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Дата должна быть в формате ГГГГ-ММ-ДД (например, 2026-04-28)")
            return
        if not self.validate_temperature(temp):
            messagebox.showerror("Ошибка", "Температура должна быть числом")
            return
        if desc.strip() == "":
            messagebox.showerror("Ошибка", "Описание погоды не может быть пустым")
            return

        # Добавляем запись
        record = {
            "date": date,
            "temperature": float(temp),
            "description": desc,
            "precipitation": precip
        }
        self.records.append(record)
        self.save_data()
        self.refresh_table()

        # Очищаем поля
        self.entry_date.delete(0, END)
        self.entry_temp.delete(0, END)
        self.entry_desc.delete(0, END)
        self.precip_var.set(False)

    # ------------------- ФИЛЬТРАЦИЯ -------------------
    def filter_records(self):
        date_filter = self.filter_date_entry.get()
        temp_filter = self.filter_temp_entry.get()

        filtered = []
        for r in self.records:
            # Фильтр по дате
            if date_filter and r["date"] != date_filter:
                continue
            # Фильтр по температуре > значение
            if temp_filter:
                try:
                    if r["temperature"] <= float(temp_filter):
                        continue
                except:
                    pass
            filtered.append(r)

        self.refresh_table(filtered)

    def reset_filter(self):
        self.filter_date_entry.delete(0, END)
        self.filter_temp_entry.delete(0, END)
        self.refresh_table()

    # ------------------- УДАЛЕНИЕ -------------------
    def delete_selected(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите запись для удаления")
            return

        # Удаляем по индексу (по позиции в текущем отображении)
        # Получаем текущие отображаемые записи
        current_items = self.table.get_children()
        indices_to_delete = []
        for item in selected:
            idx = current_items.index(item)
            indices_to_delete.append(idx)

        # Удаляем с конца, чтобы не сбить индексы
        for idx in sorted(indices_to_delete, reverse=True):
            # Получаем ID удаляемой записи
            item_id = current_items[idx]
            values = self.table.item(item_id)["values"]
            # Ищем в self.records такую же запись
            for i, rec in enumerate(self.records):
                if (rec["date"] == values[0] and
                    rec["temperature"] == float(values[1]) and
                    rec["description"] == values[2] and
                    rec["precipitation"] == values[3]):
                    del self.records[i]
                    break

        self.save_data()
        self.refresh_table()

    # ------------------- ОТОБРАЖЕНИЕ ТАБЛИЦЫ -------------------
    def create_table(self):
        frame = LabelFrame(self.root, text="Записи о погоде")
        frame.pack(fill=BOTH, expand=True, padx=10, pady=5)

        columns = ("Дата", "Температура", "Описание", "Осадки")
        self.table = ttk.Treeview(frame, columns=columns, show="headings")

        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=150)

        scrollbar = Scrollbar(frame, orient=VERTICAL, command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)

        self.table.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Кнопка удаления
        btn_delete = Button(self.root, text="❌ Удалить выбранную запись", command=self.delete_selected, bg="#ff9999")
        btn_delete.pack(pady=5)

    def refresh_table(self, records_to_show=None):
        # Очищаем таблицу
        for row in self.table.get_children():
            self.table.delete(row)

        if records_to_show is None:
            records_to_show = self.records

        for r in records_to_show:
            precip_text = "Да" if r["precipitation"] else "Нет"
            self.table.insert("", END, values=(
                r["date"],
                r["temperature"],
                r["description"],
                precip_text
            ))

    # ------------------- ИНТЕРФЕЙС ВВОДА -------------------
    def create_input_frame(self):
        frame = LabelFrame(self.root, text="Новая запись", padx=10, pady=10)
        frame.pack(fill=X, padx=10, pady=5)

        Label(frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky=W)
        self.entry_date = Entry(frame, width=15)
        self.entry_date.grid(row=0, column=1, padx=5, pady=2)

        Label(frame, text="Температура (°C):").grid(row=1, column=0, sticky=W)
        self.entry_temp = Entry(frame, width=10)
        self.entry_temp.grid(row=1, column=1, padx=5, pady=2)

        Label(frame, text="Описание погоды:").grid(row=2, column=0, sticky=W)
        self.entry_desc = Entry(frame, width=30)
        self.entry_desc.grid(row=2, column=1, padx=5, pady=2)

        self.precip_var = BooleanVar()
        Checkbutton(frame, text="Есть осадки", variable=self.precip_var).grid(row=3, column=0, columnspan=2, sticky=W)

        Button(frame, text="➕ Добавить запись", command=self.add_record, bg="#99ff99").grid(row=4, column=0, columnspan=2, pady=10)

    # ------------------- ИНТЕРФЕЙС ФИЛЬТРА -------------------
    def create_filter_frame(self):
        frame = LabelFrame(self.root, text="Фильтрация", padx=10, pady=10)
        frame.pack(fill=X, padx=10, pady=5)

        Label(frame, text="Дата (точно):").grid(row=0, column=0, sticky=W)
        self.filter_date_entry = Entry(frame, width=15)
        self.filter_date_entry.grid(row=0, column=1, padx=5)

        Label(frame, text="Температура > (градусов):").grid(row=1, column=0, sticky=W)
        self.filter_temp_entry = Entry(frame, width=10)
        self.filter_temp_entry.grid(row=1, column=1, padx=5)

        Button(frame, text="🔍 Применить фильтр", command=self.filter_records).grid(row=2, column=0, pady=5)
        Button(frame, text="🔄 Сбросить фильтр", command=self.reset_filter).grid(row=2, column=1, pady=5)

# ------------------- ЗАПУСК -------------------
if __name__ == "__main__":
    root = Tk()
    app = WeatherDiary(root)
    root.mainloop()