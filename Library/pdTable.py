from tkinter import NO, Button, Toplevel, Entry, StringVar, END, DISABLED
from tkinter.ttk import Treeview, Combobox, Label
from tkinter import messagebox as mb
import random


class pdview(Treeview):
    def __init__(self, parent, data, films, cinemas, dictionaries, widths):
        """ конструктор """
        super().__init__(parent)
        headings = [item for item in data]
        self.data = data
        self.films = films
        self.cinemas = cinemas
        self.dictionaries = dictionaries
        self['columns'] = headings

        self.column('#0', width=5, minwidth=5, stretch=NO)

        for column in headings:
            self.column(column, width=widths[column])
            self.heading(column, text=column, command=lambda col=column: self.treeview_sort_column(col, False))

        self.bind("<Double-1>", self.OnDoubleClick)

        self.fill_table(selection=None)

    def treeview_sort_column(self, col, reverse):
        """ метод сортировки """
        l = [(self.set(k, col), k) for k in self.get_children('')]
        l.sort(reverse=reverse)

        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            self.move(k, '', index)

        # reverse sort next time
        self.heading(col, command=lambda: self.treeview_sort_column(col, not reverse))

    def fill_table(self, dataset=None, selection=None):
        """ метод заполнения данными"""

        if dataset is None:
            tree = self.data
        else:
            tree = dataset

        for index, row in tree.iterrows():
            self.insert('', index, values=tuple([str(item) for item in row]))

        if selection:
            try:
                self.selection_set(self.item(selection))
            except:
                self.selection_set(self.get_children()[0])
        else:
            self.selection_set(self.get_children()[0])

    def filter_table(self, key):
        """ метод применения фильтра """
        key_columns = {'Кинотеатр': 0,
                       'Фильм': 2,
                       'Класс': 3,
                       '3D': 4,
                       'Статус': 7}

        selection = self.selection()
        selection = self.item(selection)['values'][key_columns[key]]
        x = self.get_children()
        for item in x:
            self.delete(item)

        if selection:
            y = self.data.loc[self.data[key] == selection]
            self.fill_table(dataset=y, selection=None)
        else:
            print('Ошибка определения значения для сортировки')

    def cancel_filter(self):
        """ метод отмены фильтра по строкам """
        for item in self.get_children():
            self.delete(item)
        self.fill_table()

    def sort_table(self):
        """ метод сортировки таблицы по выбранной колонке """

    def delete_item(self):
        """ метод удаления элемента из представления и из таблицы """
        selection = self.selection()
        y = self.data.loc[self.data['Билет'] == self.item(selection)['values'][-1]]
        for index, row in y.iterrows():
            self.data = self.data.drop([index])
        for item in self.get_children():
            self.delete(item)
        self.fill_table()

    def add_item(self, data):
        """ функция вставки элемента в таблицу данных """
        data_dic = {}
        for item in data.keys():
            data_dic.update({item: data[item].get()})
        data_dic['Билет'] = int(data_dic['Билет'])
        try:
            if data_dic['Цена'].strip() != '':
                data_dic['Цена'] = int(data_dic['Цена'])
            else:
                data_dic['Цена'] = 0
        except:
            return 2
        y = self.data.loc[self.data['Билет'] == data_dic['Билет']]
        if not y.empty:
            return 1

        if len(data_dic['Время']) != 5:
            print('Время')
            return 2

        try:
            if len(data_dic['Зал'].strip()) == 0:
                return 2
            else:
                data_dic['Зал'] = int(data_dic['Зал'].strip())
        except:
            return 2

        try:
            data_dic['Цена'] = int(data_dic['Цена'])
        except:
            print('Цена исключение')
            return 2


        else:
            self.data.loc[data_dic['Билет']] = data_dic
            for item in self.get_children():
                self.delete(item)
            self.fill_table()
            return 0

    def OnDoubleClick(self, event):
        """ редактирование элемента по двойному клику """
        common_width = 17
        add_width = 3
        add_item_window = Toplevel()
        add_item_window.minsize(width=250, height=340)
        item = self.selection()[0]
        set_to_edit = self.item(item, "values")
        labels = [item for item in self.data]
        lbl = []
        values = {}
        for i in range(0, len(labels)):
            values[labels[i]] = StringVar()
            lbl.append(Label(add_item_window, text=labels[i]))
            lbl[i].grid(column=0, row=i, padx=10, pady=10, sticky='w')

            if labels[i] == 'Кинотеатр':
                v = Combobox(add_item_window, values=[row[0] for index, row in self.cinemas.iterrows()],
                             textvariable=values[labels[i]], width=common_width)
            elif labels[i] == 'Время':
                v = Entry(add_item_window, textvariable=values[labels[i]])
                values[labels[i]].trace('w', lambda name, index, mode, sv=values[labels[i]],
                                                    item=v: entryUpdateEndHour(sv, item))
                values[labels[i]].set(set_to_edit[i])
            elif labels[i] == 'Фильм':
                """ живое подтверждение того, что DataFrame для строк идея плохая """
                lst = list(self.films['Фильм'])
                lst = [item.replace('[', '') for item in lst]
                lst = [item.strip("'") for item in lst]
                v = Combobox(add_item_window, values=lst, textvariable=values[labels[i]], width=common_width)

            # это можно переписать с помощью lambda в одну строку
            elif labels[i] == 'Класс':
                v = Combobox(add_item_window, values=self.dictionaries['class'], textvariable=values[labels[i]],
                             width=common_width)
            elif labels[i] == '3D':
                v = Combobox(add_item_window, values=self.dictionaries['3D'], textvariable=values[labels[i]],
                             width=common_width)
            elif labels[i] == 'Статус':
                v = Combobox(add_item_window, values=self.dictionaries['status'], textvariable=values[labels[i]],
                             width=common_width)
            else:
                v = Entry(add_item_window, textvariable=values[labels[i]], width=common_width + add_width)
                if labels[i] == 'Билет':
                    v.configure(state=DISABLED)
            values[labels[i]].trace('w', lambda name, index, mode, sv=values[labels[i]],
                                                item=v: updateBoxes(sv, item))
            values[labels[i]].set(set_to_edit[i])

            v.grid(column=1, row=i, padx=10, pady=10, sticky='w')

        ok_button = Button(add_item_window, text='Изменить', width=12,
                           command=lambda data=values, frame=add_item_window: self.save_item(data, frame))
        ok_button.grid(column=0, row=i + 1, pady=10, padx=10)

        cancel_button = Button(add_item_window, text='Отменить', command=add_item_window.destroy, width=12)
        cancel_button.grid(column=1, row=i + 1, pady=10, padx=15)

    def save_item(self, data, frame):
        """ запись нового элемента в таблицу данных """
        try:
            c = int(data['Цена'].get())
            с = int(data['Зал'].get())
        except:
            mb.showerror(title='Ошибка', message='Проверьте измененные данные')
            return

        key = int(data['Билет'].get())
        y = self.data.loc[self.data['Билет'] == key]
        if not y.empty:
            for item in data.keys():
                if item in ('Билет', 'Цена'):
                    self.data.at[y.index[0], item] = int(data[item].get())
                else:
                    self.data.at[y.index[0], item] = data[item].get()
        else:
            raise ValueError
        for item in self.get_children():
            self.delete(item)
        self.fill_table()
        frame.destroy()

    def insert_item(self):
        """ функция формирования графического интерфейса вставки нового элемента в таблицу """
        labels_lst = []
        values = {}
        entry_items = []
        count = 1

        common_width = 17
        add_width = 3
        new_item = Toplevel()
        new_item.title('Создание элемента')
        new_item.minsize(width=250, height=340)

        # lbl = Label(new_item, text='Кинотеатр')
        # lbl.grid(column=0, row=0, padx=10, pady=10, sticky='w')

        # определение текущего элемента в основном фрейме
        selection = self.selection()
        if selection:
            current_item = self.item(selection)

        labels = [item for item in self.data]

        for item in labels:
            # метки
            l = Label(new_item, text=item)
            l.grid(column=0, row=count, padx=10, pady=10, sticky='w')
            labels_lst.append(l)
            # поля ввода
            values[item] = StringVar(new_item)
            if item == 'Кинотеатр':
                v = Combobox(new_item, values=[row[0] for index, row in self.cinemas.iterrows()],
                             textvariable=values[item], width=common_width)
                v.set(current_item['values'][0])
            elif item == 'Время':
                v = Entry(new_item, textvariable=values[item])
                values[item].trace('w', lambda name, index, mode, sv=values[item], item=v: entryUpdateEndHour(sv, item))
            elif item == 'Фильм':
                """ живое подтверждение того, что DataFrame для строк идея плохая """
                lst = list(self.films[item])
                lst = [item.replace('[', '') for item in lst]
                lst = [item.strip("'") for item in lst]
                v = Combobox(new_item, values=lst, textvariable=values[item], width=common_width)
                v.current(0)

            # это можно переписать с помощью lambda в одну строку
            elif item == 'Класс':
                v = Combobox(new_item, values=self.dictionaries['class'], textvariable=values[item], width=common_width)
            elif item == '3D':
                v = Combobox(new_item, values=self.dictionaries['3D'], textvariable=values[item], width=common_width)
            elif item == 'Статус':
                v = Combobox(new_item, values=self.dictionaries['status'], textvariable=values[item],
                             width=common_width)
            else:
                v = Entry(new_item, textvariable=values[item], width=common_width + add_width)
            try:
                if v.current() < 0:
                    v.current(0)
            except:
                pass

            v.grid(column=1, row=count, padx=10, pady=10, sticky='w')
            entry_items.append(v)
            count += 1

        # присвоение случайного уникального номера билету
        values['Билет'].set(str(random.randint(0, 1000000)))

        ok_button = Button(new_item, text='Добавить', width=15,
                           command=lambda data=values, frame=new_item: self.add_to_main(data, frame))
        ok_button.grid(column=0, row=count + 1, pady=10, padx=10)

        cancel_button = Button(new_item, text='Отменить', command=new_item.destroy, width=20)
        cancel_button.grid(column=1, row=count + 1, pady=10, padx=15)

    def add_to_main(self, data, frame):
        """ добавление элемента в представление """
        if self.add_item(data) == 0:
            frame.destroy()
        elif self.add_item(data) == 1:
            mb.showerror(title='Ошибка', message='Идентификатор не уникальный')
        elif self.add_item(data) == 2:
            mb.showerror(title='Ошибка', message='Проверьте введенные данные')


def entryUpdateEndHour(sv, item):
    """ при трассировке поля ввода времени форматирует этот ввод """
    digits = list(filter(str.isdigit, sv.get()))
    sv.set('{}:{}'.format(''.join(digits[:2]), ''.join(digits[2:4])))
    item.icursor(END)


def updateBoxes(sv, item):
    pass
