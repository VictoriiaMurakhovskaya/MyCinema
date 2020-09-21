from tkinter import LEFT, BOTTOM, W, S, Toplevel, BOTH
from tkinter.ttk import Combobox, Frame, Label
import pandas as pd
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

diagrams = ['Распределение жанров', 'Диаграмма цен', 'Диаграмма популярности', 'Кластеризованная ст. диаграмма',
            'Категоризированная гистограмма', 'Диаграмма Бокса-Вискера', 'Диаграмма рассеивания']

axis_labels = {'Диаграмма цен': ['Цена', 'Количество билетов'],
               'Кластеризованная ст. диаграмма': ['Кинотеатр, класс', 'Количество сеансов'],
               'Категоризированная гистограмма': ['Цена билетов', 'Количество сеансов'],
               'Диаграмма Бокса-Вискера': ['Сеансы', 'Цена билета'],
               'Диаграмма рассеивания': ['Время начала сеанса (часы)', 'Цена билета']}


def graph_reports(window, data):
    """ функция формирования окна интерфейса формирования диаграмм согласно требований задания """
    global main, cinemas, films
    main, cinemas, films = data[0], data[1], data[2]
    graph = Toplevel(window)
    graph.title('Графические отчеты системы')
    graph.minsize(width=400, height=200)

    choose_box = Frame(graph)
    lbl = Label(choose_box, text='Выбор типа отчета')
    lbl.pack(side=LEFT, anchor=W, padx=10, pady=10)

    cmb = Combobox(choose_box, values=diagrams, width=35)
    cmb.set('Жанры')
    cmb.pack(side=LEFT, anchor=W, padx=10, pady=10)

    choose_box.pack(anchor=S, padx=10, pady=10)

    fig = Figure(figsize=(5, 4), dpi=100)
    make_fig([main, cinemas, films], fig, 0)
    canvas = FigureCanvasTkAgg(fig, master=graph)
    canvas.draw()
    canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=1)

    cmb.bind('<<ComboboxSelected>>', lambda event, canvas=canvas, ax=fig: change_canvas(event, canvas, ax))

    toolbar = NavigationToolbar2Tk(canvas, graph)
    toolbar.update()
    canvas.get_tk_widget().pack(fill=BOTH, expand=1)


def make_fig(df, fig, flag):
    """ функция формирования фигуры matplotlib согласно выбора пользователя в Combobox """
    fig.clear()
    ax = fig.subplots()

    if flag == 0:
        genres = [row[1] for index, row in df[2].iterrows()]
    elif flag == 1:
        genres = [row[5] for index, row in df[0].iterrows()]
    elif flag == 2:
        genres = [row[2] for index, row in df[0].iterrows()]

    title = diagrams[flag]
    genres_dict = {}
    if flag in range(0, 3):
        for item in genres:
            if item in genres_dict.keys():
                genres_dict[item] += 1
            else:
                genres_dict[item] = 1
        freq = [genres_dict[item] for item in genres_dict.keys()]

        if flag in [0, 2]:
            ax.pie(freq, labels=genres_dict.keys(), autopct='%1.0f%%')
        elif flag == 1:
            x = [int(item) for item in genres_dict.keys()]
            ax.bar(x, freq, width=[i*3 for i in freq], color=['red' if i > 5 else 'green' for i in freq])
    elif flag == 3:
        df1 = pd.pivot_table(data=df[0], index=['Кинотеатр', 'Класс'], values=['Зал'],
                             aggfunc=np.count_nonzero, fill_value=0)
        df1 = df1.copy()
        df1 = df1.unstack()
        width = 1
        objects = df1.index.tolist()
        x = np.ones(len(objects))
        x = 4 * np.cumsum(x)
        rects1 = ax.bar(x, df1[('Зал', 'эконом')], width, label='эконом')
        rects2 = ax.bar(x + width, df1[('Зал', 'средний')], width, label='средний')
        rects3 = ax.bar(x + 2 * width, df1[('Зал', 'люкс')], width, label='люкс')
        autolabel(rects1, ax)
        autolabel(rects2, ax)
        autolabel(rects3, ax)

    elif flag == 4:
        x = df[0]['Цена'].tolist()
        n, bins, patches = ax.hist(x, 20, density=False, facecolor='b')

    elif flag == 5:
        x = df[0]['Цена'].tolist()
        ax.boxplot(x, notch=True)

    elif flag == 6:
        # для сортировки часы извлекаем и переводим в числовой формат
        x = [int(item[0:2]) for item in df[0]['Время']]
        y = df[0]['Цена'].tolist()
        df1 = pd.DataFrame({'Время': x, 'Цена': y})
        ax.scatter('Время', 'Цена', data=df1)

    else:
        raise ValueError

    try:
        ax.set_title(title)
        ax.set_xlabel(axis_labels[title][0])
        ax.set_ylabel(axis_labels[title][1])
    except:
        pass
    return fig


def autolabel(rects, ax):
    """ функция размещения меток на столбцах диаграммы """
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{:d}'.format(int(height) if height > 0 else 0),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom')


def change_canvas(event, canvas, fig):
    """ обработчик события изменения значения Combobox """
    global films, main, cinemas
    if event:
        make_fig([main, cinemas, films], fig, diagrams.index(event.widget.get()))
        canvas.draw()
        canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=1)