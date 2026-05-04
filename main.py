import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os

class QuoteGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор случайных цитат")
        self.root.geometry("700x600")

        # Список предопределённых цитат (текст, автор, тема)
        self.quotes = [
            ("Будь изменением, которое хочешь видеть в мире.", "Махатма Ганди", "мотивация"),
            ("Жизнь — то, что с тобой происходит, пока ты строишь планы.", "Джон Леннон", "жизнь"),
            ("Не суди о своём успехе по тому, как высоко ты забрался, а по тому, как много людей ты взял с собой.", "Будда", "мудрость"),
            ("Сложно победить того, кто никогда не сдаётся.", "Бейб Рут", "спорт"),
            ("Знание — сила.", "Фрэнсис Бэкон", "учёба"),
            ("Сделай сегодня то, что другие не хотят, завтра будешь жить так, как другие не могут.", "Джаред Лето", "мотивация"),
        ]

        # Загружаем кастомные цитаты из файла (если есть)
        self.load_quotes_from_file()

        # История сгенерированных цитат (хранит кортежи: текст, автор, тема)
        self.history = []
        self.load_history()

        # --- Интерфейс ---
        # Рамка для генерации
        frame_gen = tk.LabelFrame(root, text="Генератор", padx=10, pady=10)
        frame_gen.pack(fill="x", padx=10, pady=5)

        self.btn_generate = tk.Button(frame_gen, text="🎲 Сгенерировать цитату", command=self.generate_quote, font=("Arial", 12))
        self.btn_generate.pack(pady=5)

        # Отображение текущей цитаты
        self.label_quote = tk.Label(root, text="Нажми на кнопку!", wraplength=650, font=("Arial", 11), bg="light yellow", relief="ridge", padx=10, pady=10)
        self.label_quote.pack(fill="x", padx=10, pady=5)

        # --- Фильтры ---
        frame_filter = tk.LabelFrame(root, text="Фильтры", padx=10, pady=10)
        frame_filter.pack(fill="x", padx=10, pady=5)

        tk.Label(frame_filter, text="Фильтр по автору:").grid(row=0, column=0, padx=5, pady=5)
        self.author_filter = ttk.Combobox(frame_filter, values=self.get_all_authors(), width=25)
        self.author_filter.grid(row=0, column=1, padx=5, pady=5)
        self.author_filter.bind("<<ComboboxSelected>>", lambda e: self.update_history_list())

        tk.Label(frame_filter, text="Фильтр по теме:").grid(row=1, column=0, padx=5, pady=5)
        self.topic_filter = ttk.Combobox(frame_filter, values=self.get_all_topics(), width=25)
        self.topic_filter.grid(row=1, column=1, padx=5, pady=5)
        self.topic_filter.bind("<<ComboboxSelected>>", lambda e: self.update_history_list())

        tk.Button(frame_filter, text="Сбросить фильтры", command=self.reset_filters).grid(row=2, column=0, columnspan=2, pady=5)

        # --- История ---
        frame_history = tk.LabelFrame(root, text="История цитат", padx=10, pady=10)
        frame_history.pack(fill="both", expand=True, padx=10, pady=5)

        self.history_listbox = tk.Listbox(frame_history, height=10)
        self.history_listbox.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(frame_history, orient="vertical", command=self.history_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.history_listbox.config(yscrollcommand=scrollbar.set)

        # --- Добавление новой цитаты ---
        frame_add = tk.LabelFrame(root, text="Добавить свою цитату", padx=10, pady=10)
        frame_add.pack(fill="x", padx=10, pady=5)

        tk.Label(frame_add, text="Текст цитаты:").grid(row=0, column=0, sticky="w")
        self.new_text = tk.Entry(frame_add, width=50)
        self.new_text.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(frame_add, text="Автор:").grid(row=1, column=0, sticky="w")
        self.new_author = tk.Entry(frame_add, width=30)
        self.new_author.grid(row=1, column=1, padx=5, pady=2)

        tk.Label(frame_add, text="Тема:").grid(row=2, column=0, sticky="w")
        self.new_topic = tk.Entry(frame_add, width=20)
        self.new_topic.grid(row=2, column=1, padx=5, pady=2)

        tk.Button(frame_add, text="➕ Добавить цитату", command=self.add_quote).grid(row=3, column=0, columnspan=2, pady=5)

        # --- Кнопка очистки истории ---
        tk.Button(root, text="🗑 Очистить историю", command=self.clear_history, fg="red").pack(pady=5)

        # При закрытии сохраняем всё
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Показываем историю
        self.update_history_list()

    # Получить всех уникальных авторов
    def get_all_authors(self):
        authors = set()
        for _, author, _ in self.quotes:
            authors.add(author)
        for text, author, topic in self.history:
            authors.add(author)
        return sorted(list(authors))

    # Получить все уникальные темы
    def get_all_topics(self):
        topics = set()
        for _, _, topic in self.quotes:
            topics.add(topic)
        for _, _, topic in self.history:
            topics.add(topic)
        return sorted(list(topics))

    # Генерация случайной цитаты с учётом фильтров (если они выбраны)
    def generate_quote(self):
        available = self.quotes.copy()
        # Если выбран фильтр по автору, оставляем только его цитаты
        author = self.author_filter.get()
        if author and author != "":
            available = [q for q in available if q[1] == author]
        # Фильтр по теме
        topic = self.topic_filter.get()
        if topic and topic != "":
            available = [q for q in available if q[2] == topic]

        if not available:
            messagebox.showwarning("Нет цитат", "Нет цитат с такими фильтрами!")
            return

        quote = random.choice(available)
        self.history.append(quote)  # добавляем в историю
        self.label_quote.config(text=f"«{quote[0]}»\n\n— {quote[1]} (тема: {quote[2]})")
        self.update_history_list()
        self.save_history()
        # Обновляем списки для фильтров (могли появиться новые авторы/темы)
        self.update_filter_lists()

    # Обновить отображение истории с учётом фильтров
    def update_history_list(self):
        self.history_listbox.delete(0, tk.END)
        author = self.author_filter.get()
        topic = self.topic_filter.get()
        filtered = self.history
        if author and author != "":
            filtered = [q for q in filtered if q[1] == author]
        if topic and topic != "":
            filtered = [q for q in filtered if q[2] == topic]

        for i, (text, author, topic) in enumerate(filtered, 1):
            self.history_listbox.insert(tk.END, f"{i}. {text[:60]}... — {author} [{topic}]")

    # Сброс фильтров
    def reset_filters(self):
        self.author_filter.set("")
        self.topic_filter.set("")
        self.update_history_list()

    # Обновить выпадающие списки фильтров
    def update_filter_lists(self):
        self.author_filter['values'] = self.get_all_authors()
        self.topic_filter['values'] = self.get_all_topics()

    # Добавить новую цитату (с проверкой на пустые строки)
    def add_quote(self):
        text = self.new_text.get().strip()
        author = self.new_author.get().strip()
        topic = self.new_topic.get().strip()

        if not text or not author or not topic:
            messagebox.showerror("Ошибка", "Все поля (текст, автор, тема) должны быть заполнены!")
            return

        new_quote = (text, author, topic)
        self.quotes.append(new_quote)
        self.save_quotes_to_file()
        self.update_filter_lists()
        messagebox.showinfo("Успех", "Цитата добавлена в библиотеку!")
        # Очищаем поля
        self.new_text.delete(0, tk.END)
        self.new_author.delete(0, tk.END)
        self.new_topic.delete(0, tk.END)

    # Очистить историю
    def clear_history(self):
        if messagebox.askyesno("Подтверждение", "Точно удалить всю историю?"):
            self.history = []
            self.update_history_list()
            self.save_history()
            self.label_quote.config(text="История очищена. Нажми на кнопку!")

    # Сохранить историю в JSON
    def save_history(self):
        with open("history.json", "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    # Загрузить историю из JSON
    def load_history(self):
        if os.path.exists("history.json"):
            with open("history.json", "r", encoding="utf-8") as f:
                self.history = json.load(f)

    # Сохранить все цитаты (включая добавленные) в JSON
    def save_quotes_to_file(self):
        with open("quotes.json", "w", encoding="utf-8") as f:
            json.dump(self.quotes, f, ensure_ascii=False, indent=2)

    # Загрузить кастомные цитаты
    def load_quotes_from_file(self):
        if os.path.exists("quotes.json"):
            with open("quotes.json", "r", encoding="utf-8") as f:
                self.quotes = json.load(f)

    # При закрытии сохраняем всё
    def on_close(self):
        self.save_history()
        self.save_quotes_to_file()
        self.root.destroy()

# Запуск
if __name__ == "__main__":
    root = tk.Tk()
    app = QuoteGenerator(root)
    root.mainloop()