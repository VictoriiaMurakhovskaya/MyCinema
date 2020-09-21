import xlsxwriter as xr
import os.path as osp
import os
import pandas as pd
import numpy as np
from tkinter import Toplevel, StringVar, Radiobutton, IntVar, DISABLED, NORMAL, LEFT, TOP, RIGHT, Label
from tkinter.ttk import Combobox, Entry, Button, LabelFrame, Frame
from tkinter import messagebox as mb
import threading


def trace_rb(value, widgets):
    """ трассировка и управление состояние активности виджетов ввода"""
    if widgets is None:
        return
    for i in range(0, len(widgets)):
        widgets[i].configure(state=NORMAL if i == value.get() else DISABLED)


def ask_open_xlsx(filename):
    if mb.askyesno(title='Открыть', message='Открыть сформированную таблицу?'):
        t1 = threading.Thread(target=open_xlsx, args=[filename])
        t1.start()


def make_easy_report(df, column, values, value_var, frame):
    """ формирование и выгрузка простого отчета """
    filename = 'easy_report.xlsx'
    column = column[value_var.get()]
    value = values[value_var.get()].get()
    y = df.f[df[column] == value]
    y.to_excel('Output/' + filename, sheet_name='Простой отчет', header=True, index=True)
    frame.destroy()
    ask_open_xlsx(filename)


def easy_report(df, cinemas, films, dicts):
    """ интерфейс выбора параметров простого отчета """
    report = Toplevel()
    options = [item for item in df]
    values = []
    values_widgets = []
    count = 0
    value_var = IntVar()
    value_var.set(0)

    for item in options[:-1]:
        Radiobutton(report, text=item, variable=value_var, value=count,
                    command=lambda num=value_var, w=values_widgets: trace_rb(num, w)) \
            .grid(column=0, row=count, padx=(15, 5), pady=5, sticky='w')

        values.append(StringVar())
        if item == 'Кинотеатр':
            e = Combobox(report, values=[row[0] for index, row in cinemas.iterrows()], textvariable=values[count])
        elif item == 'Фильм':
            e = Combobox(report, values=[row[0] for index, row in films.iterrows()], textvariable=values[count])
        elif item == 'Класс':
            e = Combobox(report, values=dicts['class'], textvariable=values[count])
        elif item == '3D':
            e = Combobox(report, values=dicts['3D'], textvariable=values[count])
        elif item == 'Статус':
            e = Combobox(report, values=dicts['status'], textvariable=values[count])
        else:
            e = Entry(report, textvariable=values[count])
        try:
            e.current(0)
        except:
            pass
        e.grid(column=1, row=count, padx=(15, 5), pady=5, sticky='e')
        values_widgets.append(e)

        count += 1

    trace_rb(IntVar(0), values_widgets)

    btnOk = Button(report, text='Сформировать', width=15, command=lambda data=df, column=options,
                                                                         v1=values, v2=value_var,
                                                                         fr=report: make_easy_report(df, column, v1, v2,
                                                                                                     fr))
    btnOk.grid(column=0, row=count + 1, padx=10, pady=10)

    btnCancel = Button(report, text='Отменить', width=12, command=lambda: report.destroy())
    btnCancel.grid(column=1, row=count + 1, padx=10, pady=15)


def make_pivot(df, dicts):
    """ формирование сводной таблицы """
    report = Toplevel()
    radio = Frame(report)
    buttons = Frame(report)
    param1 = LabelFrame(radio, text='1-й параметр')
    param2 = LabelFrame(radio, text='2-й параметр')
    options = [item for item in df][:-1]
    options.pop(options.index('Цена'))
    value_var_1 = IntVar()
    value_var_2 = IntVar()
    count = 0
    for item in options:
        Radiobutton(param1, text=item, variable=value_var_1, value=count,
                    command=lambda num=value_var_1: trace_rb(num, None)) \
            .pack(side=TOP, anchor='w')
        Radiobutton(param2, text=item, variable=value_var_2, value=count,
                    command=lambda num=value_var_2: trace_rb(num, None)) \
            .pack(side=TOP, anchor='w')
        count += 1
    param1.pack(side=LEFT, padx=(20, 5), pady=(20, 10))

    res = {'Минимум': np.min, 'Максимум': np.max}
    picker = Frame(report)
    Label(picker, text='Метод агрегации') \
        .pack(side=LEFT, anchor='w', padx=10, pady=10)
    method = StringVar(report)
    m_combo = Combobox(picker, values=[item for item in res.keys()], textvariable=method)
    m_combo.current(0)
    m_combo.pack(side=LEFT, padx=10, pady=10, anchor='e')

    Button(buttons, text='Сформировать',
           command=lambda v0=df, v1=value_var_1, v2=value_var_2, v3=options, fr=report, m=method, m_dic=res:
           pivot_export(v0, v1, v2, v3, fr, m, m_dic)) \
        .pack(side=LEFT, anchor='w', padx=10, pady=10)
    param2.pack(side=LEFT, padx=(5, 20), pady=(20, 10))
    Button(buttons, text='Закрыть', command=lambda: report.destroy()) \
        .pack(side=RIGHT, anchor='e', padx=10, pady=10)

    radio.pack(side=TOP)
    picker.pack(side=TOP)
    buttons.pack(side=TOP)
    value_var_1.set(0)
    value_var_2.set(0)


def pivot_export(df, v1, v2, options, frame, m, m_dic):
    """ экспорт сводной таблицы """
    v1 = v1.get()
    v2 = v2.get()
    if v1 == v2:
        mb.showerror(title='Ошибка', message='Параметры одинаковые')
        return
    filename = 'pivot_table.xlsx'
    method = m.get()
    method = m_dic[method]
    df1 = pd.pivot_table(data=df, index=[options[v1], options[v2]], values=['Цена'], aggfunc={'Цена': [method]})
    df1.to_excel('Output/' + filename, sheet_name='Pivot table', header=True, index=True)
    frame.destroy()
    ask_open_xlsx(filename)


def open_xlsx(filename):
    """ функция открытия файла отчета в отдельном процессе """
    try:
        os.system('Output\\' + filename)
    except:
        pass


def make_statistics(flag):
    """ формирование статистики """
    print(flag)


def text_report_old(df):
    """ формирование статистики """
    global stat
    items_dic = {}
    headers_dic = {}
    if not osp.isdir('out'):
        os.mkdir('out')

    filename = 'statistics.xlsx'
    sheetname = ['Qualitative', 'Quantitative']

    # формирование статистики для качественной переменной
    print(stat)
    freq = df[stat].value_counts()
    rel_freq = freq / sum(freq)
    headers_dic.update({'Qualitative': ['Переменная', 'Абсолютная частота', 'Относительная частота']})
    frame = {'Значение': freq.index, 'Частота': freq, 'Относительная частота': rel_freq}
    df1 = pd.DataFrame(frame)
    items_dic.update({'Qualitative': df1})

    # формирование статистики для количественной переменной
    headers_dic.update({'Quantitative': ['Статистика', 'Значение']})
    price = df['Цена'].copy()

    # формирование статистики для количественной переменной (количественная переменная одна - цена билета)
    dic_tmp = {'Статистика': ['Максимум', 'Минимум', 'Среднее', 'Выборочная дисперсия', 'Стандартное отклонение']}
    dic_tmp.update({'Значения': [price.max(), price.min(), price.mean(), price.var(), price.std()]})
    df2 = pd.DataFrame(dic_tmp)
    items_dic.update({'Quantitative': df2})

    wb = xr.Workbook('Output/' + filename)
    for item in sheetname:
        wf = wb.add_worksheet(item)
        write_header(wb, wf, headers_dic[item])
        write_items(wb, wf, items_dic[item])
    wb.close()
    ask_open_xlsx(filename)


def write_header(wb, wf, headers):
    """ формирование заголовка при экспорте отчета в Excel """
    format_header = wb.add_format({'align': 'center',
                                   'valign': 'vcenter',
                                   'text_wrap': True,
                                   'bold': True,
                                   'border': 1})
    format_header.set_font_size(11)
    count = 0
    for item in headers:
        wf.write(0, count, item, format_header)
        count += 1


def write_items(wb, wf, df):
    """ формирование строки при экспорте отчета в Excel """
    format_lb = wb.add_format({'text_wrap': False,
                               'align': 'right',
                               'valign': 'vcenter',
                               'border': 1,
                               'bold': False})
    format_lb.set_font_size(10)
    format_lb.set_indent(1)

    c_row, c_col = 1, 0
    for index, row in df.iterrows():
        for item in row:
            wf.write(c_row, c_col, item, format_lb)
            c_col += 1
        c_col = 0
        c_row += 1


def statistics(df, dictionaries):
    """ фомрмирование статистик """
    global stat
    report = Toplevel()
    qty = StringVar(report)
    headers = [item for item in df if item not in ['Цена', 'Билет', 'Время']]
    q1 = LabelFrame(report, text='Качественные')
    q2 = LabelFrame(report, text='Количественные')
    choice = Combobox(q1, values=headers, textvariable=qty)
    qty.trace('w', lambda name, index, mode, sv=qty: updateBoxes(sv))
    qty.set(headers[0])
    choice.current(0)
    choice.pack(side=LEFT, padx=5, pady=5)
    q1.pack(side=TOP, padx=10, pady=10)
    choice2 = Combobox(q2, values=['Цена'])
    choice2.pack(side=LEFT, padx=5, pady=5)
    choice2.current(0)
    choice2.config(state=DISABLED)
    q2.pack(side=TOP, padx=10, pady=10)
    bframe = Frame(report)
    Button(bframe, text='Сформировать', command=lambda frame=df: text_report_old(frame))\
        .pack(side=LEFT, padx=10, pady=10)
    Button(bframe, text='Закрыть', command=lambda: report.destroy())\
        .pack(side=LEFT, padx=10, pady=10)
    bframe.pack(side=TOP)


def updateBoxes(sv):
    """ обработка события при выборе RadioButton """
    global stat
    stat = sv.get()