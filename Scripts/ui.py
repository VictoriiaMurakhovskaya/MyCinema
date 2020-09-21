from tkinter import Tk, NO, LEFT, W, Toplevel, StringVar, END, TOP, Label, Menu, BOTTOM, Button
from tkinter.ttk import Treeview, Combobox, Frame, LabelFrame, Entry, Scrollbar
import pandas as pd
from Library.text_reports import easy_report, make_pivot, statistics
import configparser
import os.path as osp
from Library.graphs import graph_reports
from Library.pdTable import pdview
from tkinter.colorchooser import askcolor

color_set = []


def on_closing(files):
    """ обработчик события закрытия основного окна программы """
    global color_set
    mainview.data.to_pickle(files[0])
    mainview.films.to_pickle(files[1])
    mainview.cinemas.to_pickle(files[2])

    config = configparser.ConfigParser()
    config.read('config.cfg ')
    config['Colors']['foreground'] = color_set[0].get()
    config['Colors']['background'] = color_set[1].get()
    with open('config.cfg', "w") as config_file:
        config.write(config_file)

    window.destroy()


def report_go(flag):
    """ функция запуска текстовых и графических отчетов
        используется для сокращения вызовов функция в обработчиках кнопок """
    if flag == 1:
        if reports_box.current() == 0:
            easy_report(mainview.data, mainview.cinemas, mainview.films, dictionaries)
        elif reports_box.current() == 1:
            statistics(mainview.data, dictionaries)
        elif reports_box.current() == 2:
            make_pivot(mainview.data, dictionaries)
        else:
            raise ValueError
    elif flag == 2:
        graph_reports(window, (mainview.data, mainview.cinemas, mainview.films))


def create_config():
    """ функция создания конфигурационного файла, если таковой отсутствует """
    config = configparser.ConfigParser()

    # файлы данных программы
    config.add_section("Files")
    config.set("Files", "maindata", 'Data/Main.pkl')
    config.set("Files", "films", 'Data/Films.pkl')
    config.set("Files", "cinemas", 'Data/Cinema.pkl')

    # наборы словарей в программе
    config.add_section('Dictionaries')
    config.set('Dictionaries', 'class', 'люкс; средний; эконом')
    config.set('Dictionaries', '3D', 'да; нет')
    config.set('Dictionaries', 'status', 'забронирован; идёт; завершился')

    config.add_section('Colors')
    config.set('Colors', 'foreground', '#FFFFFF')
    config.set('Colors', 'background', '#000000')

    with open('config.cfg', "w") as config_file:
        config.write(config_file)


def read_config():
    """ функция чтения конфигурационного файла """
    global color_set
    config = configparser.ConfigParser()
    config.read('config.cfg')
    files_paths = [config.get("Files", "maindata"), config.get("Files", "films"), config.get("Files", "cinemas")]
    dictionaries = {'class': [item.strip() for item in config.get('Dictionaries', 'class').split(';')],
                    '3D': [item.strip() for item in config.get('Dictionaries', '3D').split(';')],
                    'status': [item.strip() for item in config.get('Dictionaries', 'status').split(';')]}
    color_set[0].set(config.get('Colors', 'foreground'))
    color_set[1].set(config.get('Colors', 'background'))
    return files_paths, dictionaries, color_set[0].get(), color_set[1].get()


def filter_table(event):
    """ функция применения фильтра таблицы """
    mainview.filter_table(event.widget.get())


def pick_color(flag, place):
    """ вызов ColorPicker """
    global color_set
    _, color = askcolor()
    color_set[flag].set(color)
    if flag == 0:
        place['fg'] = color
    elif flag == 1:
        place['bg'] = color
    else:
        raise ValueError


def run_color_picker():
    """ графический интерфейс настройки цветовой схемы """
    global color_set, window
    color_picker = Toplevel(window)
    top_frame = Frame(color_picker)
    left_frame = Frame(top_frame)
    right_frame = Frame(top_frame)
    show_area = Label(left_frame, text='Пример текста')
    show_area['fg'] = color_set[0].get()
    show_area['bg'] = color_set[1].get()
    Button(right_frame, text='Цвет текста', command=lambda z=0, place=show_area: pick_color(z, place))\
        .pack(side=TOP, pady=5)
    Button(right_frame, text='Цвет фона', command=lambda z=1, place=show_area: pick_color(z, place))\
        .pack(side=TOP, pady=5)
    show_area.pack(side=LEFT, padx=10, pady=10)
    left_frame.pack(side=LEFT, padx=10, pady=10)
    right_frame.pack(side=LEFT, padx=10, pady=10)
    top_frame.pack(side=TOP)


def show_table(flag, tables):
    """ графический интерфейс просмотра справочников """
    catalog = Toplevel(window)
    catalog.title('Просмотр справочников')
    if flag == 1:
        df = tables[0]
        df = df.merge(tables[1], how='outer')
        df = df.merge(tables[2], how='outer')
        widths = {'Кинотеатр': 120, 'Время': 50, 'Фильм': 100, 'Класс': 60, '3D': 30, 'Цена': 40, 'Зал': 25,
                  'Статус': 90, 'Билет': 40, 'Жанр': 50, 'Вместимость': 40, 'Рейтинг': 40}
    elif flag == 2:
        df = tables[0]
        widths = {'Фильм': 100, 'Жанр': 80}
    elif flag == 3:
        df = tables[0]
        widths = {'Кинотеатр': 120, 'Вместимость': 50, 'Рейтинг': 50}
    headings = [item for item in df]
    view = Treeview(catalog, selectmode ='browse')
    view['columns'] = headings
    view.column('#0', width=5, minwidth=5, stretch=NO)
    for column in headings:
        view.column(column, width=widths[column])
        view.heading(column, text=column)
    for index, row in df.iterrows():
        view.insert('', index, values=tuple([str(item) for item in row]))

    Button(catalog, text='Закрыть', command=lambda: catalog.destroy())\
        .pack(side=BOTTOM, padx=(10, 10), pady=(5, 15))
    view.pack(side=TOP, pady=(20, 10), padx=10)



def main():
    """ основная функция графического интерфейса программы """
    global mainview, main, films, cinemas, window, dictionaries, textrep, reports_box, color_set
    window = Tk()
    window.title('Основное системное окно')
    window.geometry('600x380')

    color_set = [StringVar(), StringVar()]

    # установка начальных параметров
    if not osp.exists('config.cfg'):
        create_config()
    files, dictionaries, color_fg, color_bg = read_config()

    # основное представление таблицы
    try:
        widths = {'Кинотеатр': 120, 'Время': 50, 'Фильм': 100, 'Класс': 60, '3D': 30, 'Цена': 40, 'Зал': 25,
                  'Статус': 90, 'Билет': 40}
        mainview = pdview(window, pd.read_pickle(files[0]), pd.read_pickle(files[1]),
                          pd.read_pickle(files[2]), dictionaries, widths)
    except IOError:
        SystemExit(101)

    # добавление меню
    mainmenu = Menu(window)
    window.config(menu=mainmenu)

    optionmenu = Menu(mainmenu, tearoff=0)
    optionmenu.add_command(label='Полная таблица',
                           command=lambda flag=1, tables=[mainview.data, mainview.films, mainview.cinemas]:
                           show_table(flag, tables))
    optionmenu.add_separator()
    optionmenu.add_command(label='Фильмы',
                           command=lambda flag=2, tables=[mainview.films]: show_table(flag, tables))
    optionmenu.add_command(label='Кинотеатры',
                           command=lambda flag=3, tables=[mainview.cinemas]: show_table(flag, tables))

    mainmenu.add_cascade(label='Справочники', menu=optionmenu)
    mainmenu.add_command(label='Цвета', command=run_color_picker)
    mainmenu.add_command(label='Выход', command=lambda f=files: on_closing(f))

    top_frame = Frame(window)
    top_frame.pack(anchor=W)

    # добавление кнопок интерфейса
    # кнопки добавить/удалить
    ins_del_frame = LabelFrame(top_frame, text='Добавление/удаление')

    ins_item = Button(ins_del_frame, text='Добавить', width=15, fg=color_fg, bg=color_bg,
                      command=lambda: mainview.insert_item())
    ins_item.pack(side=LEFT, padx=5, pady=5)

    del_item = Button(ins_del_frame, text='Удалить', width=15, fg=color_fg, bg=color_bg,
                      command=lambda: mainview.delete_item())
    del_item.pack(side=LEFT, padx=5, pady=5)

    ins_del_frame.pack(side=LEFT, padx=10, pady=10)

    # добавление функциии сортировки и кнопки отмены сортировки
    filter_frame = LabelFrame(top_frame, text='Фильтр')
    sort_box = Combobox(filter_frame, values=['Кинотеатр', 'Фильм', 'Класс', '3D', 'Статус'])
    sort_box.set('Класс')
    sort_box.bind('<<ComboboxSelected>>', filter_table)
    sort_box.pack(side=LEFT, padx=5, pady=5)

    cancel_sort = Button(filter_frame, text='X', width=3, command=lambda: mainview.cancel_filter())
    cancel_sort.pack(side=LEFT, padx=5, pady=5)
    filter_frame.pack(side=LEFT, padx=10, pady=10)

    mainview.pack(padx=10)

    # добавление вызова интерфейса отчетов
    bot_frame = Frame(window)
    bot_frame_text = LabelFrame(bot_frame, text='Текстовые отчеты')
    textrep = StringVar(window)
    reports_box = Combobox(bot_frame_text, values=['Простой отчет', 'Статистический отчет', 'Сводная таблица'],
                           textvariable=textrep)
    reports_box.current(0)
    reports_box.pack(side=LEFT, padx=5, pady=5)
    reports_button = Button(bot_frame_text, text='Сформировать', width=15, fg=color_fg, bg=color_bg,
                            command=lambda flag=1: report_go(flag))
    reports_button.pack(side=LEFT, padx=5, pady=5)
    bot_frame_text.pack(side=LEFT)
    graph_button = Button(bot_frame, text='Графические отчеты', width=25, fg=color_fg, bg=color_bg,
                          command=lambda flag=2: report_go(flag))
    graph_button.pack(side=LEFT, padx=10, pady=10)

    bot_frame.pack(padx=10, pady=10, anchor=W)

    window.protocol("WM_DELETE_WINDOW", lambda f=files: on_closing(f))
    window.mainloop()
