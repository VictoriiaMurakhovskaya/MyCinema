import sys
from Scripts import util, ui


def main():
    """ основной метод запуска приложения
    обрабатывает допустимые аргументы командной строки """
    if sys.argv[1] == '-m':
        ui.main()
    elif sys.argv[1] == '-u':
        util.main()
    else:
        print('Invalid argument')


if __name__ == '__main__':
    main()