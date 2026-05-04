import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime

# --- Основная логика приложения ---
class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("600x500")

        # --- Поля ввода ---
        tk.Label(root, text="Сумма:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_sum = tk.Entry(root)
        self.entry_sum.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(root, text="Категория:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.combo_category = ttk.Combobox(root, values=["Еда", "Транспорт", "Развлечения", "Жильё", "Здоровье"])
        self.combo_category.grid(row=1, column=1, padx=5, pady=5)
        self.combo_category.current(0)

        tk.Label(root, text="Дата (ГГГГ-ММ-ДД):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.entry_date = tk.Entry(root)
        self.entry_date.grid(row=2, column=1, padx=5, pady=5)

        # --- Кнопка добавления ---
        btn_add = tk.Button(root, text="Добавить расход", command=self.add_expense)
        btn_add.grid(row=3, columnspan=2, padx=5, pady=5)

        # --- Таблица расходов ---
        self.tree = ttk.Treeview(root, columns=("sum", "category", "date"), show='headings')
        self.tree.heading("sum", text="Сумма")
        self.tree.heading("category", text="Категория")
        self.tree.heading("date", text="Дата")
        self.tree.grid(row=4, columnspan=2, padx=5, pady=5, sticky="nsew")

        # Настройка веса сетки для растягивания таблицы
        root.grid_rowconfigure(4, weight=1)
        root.grid_columnconfigure(1, weight=1)

        # --- Поля для подсчёта суммы за период ---
        tk.Label(root, text="С:").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.entry_date_from = tk.Entry(root)
        self.entry_date_from.grid(row=5, column=1, padx=5, pady=5)

        tk.Label(root, text="По:").grid(row=6, column=0, padx=5, pady=5, sticky="e")
        self.entry_date_to = tk.Entry(root)
        self.entry_date_to.grid(row=6, column=1, padx=5, pady=5)

        btn_calc = tk.Button(root, text="Посчитать сумму", command=self.calculate_sum)
        btn_calc.grid(row=7, columnspan=2, padx=5, pady=5)

        # --- Поля для фильтрации ---
        self.filter_category = tk.StringVar()
        self.filter_category.set("Все")
        
        tk.Label(root, text="Фильтр по категории:").grid(row=8, column=0, padx=5, pady=5, sticky="e")
        filter_combo = ttk.Combobox(root, textvariable=self.filter_category,
                                    values=["Все", "Еда", "Транспорт", "Развлечения", "Жильё", "Здоровье"])
        filter_combo.grid(row=8, column=1, padx=5, pady=5)
        
        self.filter_date = tk.StringVar()
        
        tk.Label(root, text="Фильтр по дате (ГГГГ-ММ-ДД):").grid(row=9, column=0, padx=5, pady=5, sticky="e")
        filter_date_entry = tk.Entry(root)
        filter_date_entry.grid(row=9, column=1, padx=5, pady=5)
        
        btn_filter = tk.Button(root, text="Фильтровать", command=self.filter_expenses)
        btn_filter.grid(row=10, columnspan=2, padx=5, pady=5)

         # --- Кнопки сохранения/загрузки ---
        btn_save = tk.Button(root, text="Сохранить в JSON", command=self.save_to_json)
        btn_save.grid(row=11, column=0, padx=5, pady=10)

        btn_load = tk.Button(root, text="Загрузить из JSON", command=self.load_from_json)
        btn_load.grid(row=11, column=1, padx=5, pady=10)

    # --- Логика добавления расхода ---
    def add_expense(self):
        try:
            sum_value = float(self.entry_sum.get())
            if sum_value <= 0:
                raise ValueError("Сумма должна быть положительной")
            category = self.combo_category.get()
            date = self.entry_date.get()
            datetime.strptime(date, "%Y-%m-%d")  # Проверка формата даты

            self.tree.insert("", "end", values=(sum_value, category, date))
            
            # Очистка полей после добавления
            self.entry_sum.delete(0, 'end')
            self.entry_date.delete(0,'end')
            
            messagebox.showinfo("Успех", "Расход добавлен!")
            
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))

    # --- Подсчёт суммы за период ---
    def calculate_sum(self):
        try:
            date_from = datetime.strptime(self.entry_date_from.get(), "%Y-%m-%d")
            date_to = datetime.strptime(self.entry_date_to.get(), "%Y-%m-%d")
            
            total = 0.0
            for child in self.tree.get_children():
                values = self.tree.item(child)['values']
                expense_date = datetime.strptime(values[2], "%Y-%m-%d")
                if date_from <= expense_date <= date_to:
                    total += float(values[0])
            
            messagebox.showinfo("Итоговая сумма", f"Сумма расходов с {date_from.date()} по {date_to.date()}: {total:.2f} ₽")
            
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Проверьте формат дат (ГГГГ-ММ-ДД)")

    # --- Фильтрация расходов ---
    def filter_expenses(self):
        selected_cat = self.filter_category.get()
        selected_date = self.filter_date.get()
        
        for child in self.tree.get_children():
            values = self.tree.item(child)['values']
            show = True

            if selected_cat != "Все" and values[1] != selected_cat:
                show = False

            if selected_date and values[2] != selected_date:
                show = False

            self.tree.move(child, '', index='end') # Обновляем порядок
            if show:
                self.tree.item(child , tags='show')
            else:
                self.tree.item(child , tags='hide')
        
         # Скрываем/показываем строки в зависимости от тегов
         for child in self.tree.get_children():
             tags = self.tree.item(child)['tags']
             if 'hide' in tags:
                 self.tree.delete(child)
             elif 'show' in tags:
                 pass # Оставляем видимыми

    # --- Сохранение в JSON ---
    def save_to_json(self):
        data = []
        for child in self.tree.get_children():
            values = self.tree.item(child)['values']
            data.append({
                "sum": values[0],
                "category": values[1],
                "date": values[2]
            })
        
        with open("expenses.json", "w") as f:
            json.dump(data, f)
        
         messagebox.showinfo("Сохранено", "Данные успешно сохранены в expenses.json")

    # --- Загрузка из JSON ---
    def load_from_json(self):
         try:
             with open("expenses.json", "r") as f:
                 data = json.load(f)
             
             # Очищаем текущую таблицу перед загрузкой
             for child in self.tree.get_children():
                 self.tree.delete(child)
             
             for item in data:
                 self.tree.insert("", "end", values=(item["sum"], item["category"], item["date"]))
             
             messagebox.showinfo("Загружено", "Данные успешно загружены из expenses.json")
             
         except FileNotFoundError:
             messagebox.showerror("Ошибка", "Файл expenses.json не найден.")
         except json.JSONDecodeError:
             messagebox.showerror("Ошибка", "Файл expenses.json повреждён или пуст.")


# --- Запуск приложения ---
if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()