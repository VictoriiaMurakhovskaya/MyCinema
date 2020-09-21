from tkinter import Tk, Label, Button, CENTER, LabelFrame, TOP, LEFT, RIGHT, X
from tkinter.ttk import Frame
from tkinter import filedialog as fd
from tkinter import messagebox as mb
import pandas as pd
import xlsxwriter

sheets = ['Main', 'Films', 'Cinema']


def choose_file(num):
    """ функция выбора файла при нажатии соответствующей кнопки """
    global data_file, pickle_file
    def_ext = '.xlsx'
    f_types = [('Excel таблицы', '*.xlsx'),
               ('Excel таблицы (2007)', '*.xls')]

    if num == 1:
        df = fd.askopenfilename(defaultextension=def_ext, filetypes=f_types)
    elif num == 2:
        df = fd.asksaveasfile(mode='w', defaultextension=def_ext, filetypes=f_types)
        df = df.name
    else:
        raise ValueError

    if df is None:
        mb.showwarning(title='Ошибка', message='Некорректно выбран файл')
        return

    if len(df) > 20:
        str_file_name = '...' + df[-20:]
    else:
        str_file_name = df

    if num == 1:
        lbl1['text'] = str_file_name
        data_file = df
    elif num == 2:
        lbl1_2['text'] = str_file_name
        pickle_file = df
    else:
        raise ValueError


def choose_dir(num):
    """ функция выбора директории при нажатии соответствующей кнопки """
    global out_dir, out_dir_save
    od = fd.askdirectory()
    if od == '':
        mb.showwarning(title='Ошибка', message='Некорректно выбрана директория')
        return
    if len(od) > 20:
        str_out_dir = '...' + od[-20:]
    else:
        str_out_dir = od
    if num == 1:
        lbl2['text'] = str_out_dir
        out_dir = od
    elif num == 2:
        lbl2_2['text'] = str_out_dir
        out_dir_save = od
    else:
        raise ValueError


def load_data():
    """ функция загрузки данных из формата Excel в Pickle файлы """
    global data_file, sheets
    tables = {sheet: pd.read_excel(data_file, sheet) for sheet in sheets}
    try:
        for item in tables.keys():
            tables[item].to_pickle(out_dir + '/' + item + '.pkl')
        mb.showinfo(title='Информация', message='Загрузка завершена')
    except:
        mb.showwarning(title='Ошибка', message='Файлы не записаны')


def export_data():
    """ функция выгрузки данных из формата Pickel в Excel """
    try:
        tables = {sheet: pd.read_pickle(out_dir_save + '/' + sheet+'.pkl') for sheet in sheets}
    except:
        mb.showwarning(title='Ошибка', message='Неудачная выгрузка данных')
        return

    wb = xlsxwriter.Workbook(pickle_file)
    wf = {item: wb.add_worksheet(item) for item in sheets}

    for item in sheets:
        col_num = 0
        for column in tables[item]:
            wf[item].write(0, col_num, column)
            row_num = 1
            columnsObj = tables[item][column]
            for item_to_write in columnsObj:
                wf[item].write(row_num, col_num, item_to_write)
                row_num += 1
            col_num += 1
    try:
        wb.close()
        mb.showinfo(title='Информация', message='Выгрузка завершена')
    except:
        mb.showwarning(title='Ошибка', message='Не записан файл')


def main():
    """ основная функция - графический интерфейс утилиты"""
    global lbl1, lbl2, lbl1_2, lbl2_2
    window = Tk()
    window.title('Утилита загрузки/выгрузки')
    window.geometry('380x280')

    # область загрузки данных
    loaddata = LabelFrame(window, text='Загрузить данные')

    # фрейм надписей
    labelload = Frame(loaddata)
    lbl1 = Label(labelload, text='Начальный файл', justify=LEFT)
    lbl1.pack(side=TOP, padx=5, pady=5, anchor='w')
    lbl2 = Label(labelload, text='Директория сохранения', justify=LEFT)
    lbl2.pack(side=TOP, padx=5, pady=5, anchor='w')
    labelload.pack(side=LEFT, padx=10, pady=10)

    # фрейм кнопок
    buttonload = Frame(loaddata)
    btn_file = Button(buttonload, text="...", width=3, command=lambda: choose_file(1))
    btn_file.pack(side=TOP, pady=5, padx=5, anchor='e')
    btn_dir = Button(buttonload, text="...", width=3, command=lambda: choose_dir(1))
    btn_dir.pack(side=TOP, pady=5, padx=5, anchor='e')
    buttonload.pack(side=LEFT, padx=10, pady=10)

    # большая кнопка
    btn_load = Button(loaddata, text='Загрузить данные', justify=CENTER, command=load_data)
    btn_load.pack(side=RIGHT, padx=5, pady=5)

    loaddata.pack(side=TOP, padx=10, pady=10, fill=X)

    # область выгрузки данных
    savedata = LabelFrame(window, text='Выгрузить данные')
    labelsave = Frame(savedata)
    buttonsave = Frame(savedata)

    lbl1_2 = Label(labelsave, text='Файл выгрузки', justify=LEFT)
    lbl1_2.pack(side=TOP, padx=5, pady=5, anchor='w')
    lbl2_2 = Label(labelsave, text='Директория файлов', justify=LEFT)
    lbl2_2.pack(side=TOP, padx=5, pady=5, anchor='w')
    labelsave.pack(side=LEFT, padx=10, pady=10)

    btn_file_2 = Button(buttonsave, text="...", width=3, command=lambda: choose_file(2))
    btn_file_2.pack(side=TOP, padx=5, pady=5, anchor='e')
    btn_dir_2 = Button(buttonsave, text="...", width=3, command=lambda: choose_dir(2))
    btn_dir_2.pack(side=TOP, padx=5, pady=5, anchor='e')
    buttonsave.pack(side=LEFT, padx=10, pady=10)

    btn_save = Button(savedata, text='Сохранить данные', justify=CENTER, command=export_data)
    btn_save.pack(side=RIGHT, padx=5, pady=5)
    savedata.pack(side=TOP, padx=10, pady=10, fill=X)

    window.mainloop()
