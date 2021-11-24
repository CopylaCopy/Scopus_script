# -*- coding: utf-8 -*-
from Create_template import Ui_Dialog
from PyQt5 import QtCore, QtGui, QtWidgets
import datetime
from functools import partial
from filebrowser import Ui_MainWindow
from make_template import load
import sys
import os
cond = QtCore.QWaitCondition()
mutex = QtCore.QMutex()

class MyFileBrowser(Ui_MainWindow, QtWidgets.QMainWindow):
    # закрыть окно, если основная программа закрыта
    def __init__(self, maya=False):
        super(MyFileBrowser, self).__init__()
        self.setupUi(self)
        self.maya = maya
        self.treeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self.context_menu)
        self.populate()
        
    def populate(self):
        path = r""
        self.model = QtWidgets.QFileSystemModel()
        self.model.setRootPath((QtCore.QDir.rootPath()))
        self.treeView.setModel(self.model)
        self.treeView.setRootIndex(self.model.index(path))
        self.treeView.setSortingEnabled(True)

    def context_menu(self):
        menu = QtWidgets.QMenu()
        cursor = QtGui.QCursor()
        menu.exec_(cursor.pos())
        
    def button_click(self):
        self.file_path =self.model.filePath(self.treeView.currentIndex())

        
class customstdout(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)
    def __init__(self):
        QtCore.QObject.__init__(self)

    def write(self, text):
        self.textWritten.emit(str(text))
        
    def flush(self):
        pass

        
class customstdin(QtCore.QObject):
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.text = None

    def readline(self):
        mutex.lock()
        cond.wait(mutex)
        mutex.unlock()
        print(self.text)
        return self.text

class WorkerThread(QtCore.QThread):
    '''Does the work'''
    finished = QtCore.pyqtSignal()
    def __init__(self, ui):
        super(WorkerThread, self).__init__()
        self.ui = ui
        self.output = customstdout()
        self.input = customstdin()
        self.running = True
        
    def run(self):
        '''This starts the thread on the start() call'''
        load(self.ui, self.output, self.input)
        self.finished.emit()


class Activity(Ui_Dialog):
    def __init__(self):
        self.filepath = None
        self.names = []
        self.target_dir = None
        self.mode = None
        
    def push_the_button_search(self, num):
        """вызвать просмотрщик файлов в системе запуска Вернуть адрес файла присвоить его переменной и вывести в окно"""
        self.fb = MyFileBrowser()
        self.fb.show()
        self.fb.pushButton.clicked.connect(self.fb.button_click)
        if num ==1:
            self.fb.pushButton.clicked.connect(self.insert_target)
        elif num == 2:
            self.fb.pushButton.clicked.connect(self.insert_input)
        
    def insert_target(self):
        self.textBrowser_2.clear()
        self.textBrowser_2.insertPlainText(self.fb.file_path)
        self.target_dir = self.fb.file_path
        self.fb.close()
        
    def insert_input(self):
        self.textBrowser_3.clear()
        self.textBrowser_3.insertPlainText(self.fb.file_path)
        self.filepath = self.fb.file_path
        self.fb.close()
        
    def push_the_button_add(self):
        """Взять строку из диалогового окна, добавить ее к переменной, вывести на экран в список""" 
        text = self.lineEdit_4.text()
        if text != '':
            for i in text.split('\n'):
                self.textBrowser.insertPlainText(i + '\n')
                self.names.append(i)
        self.lineEdit_4.clear()
        
    def push_the_button_delete(self): 
        """Очистить переменную, очистить экран""" 
        self.textBrowser.clear() 
        self.names = []
        
    def Compose(self):
        self.name = self.lineEdit.text()
        if not self.name:
            self.name = 'John Dow'
        self.date = self.lineEdit_2.text()
        if not self.date:
            date = datetime.date.today()
            self.date = f'{date.day}.{date.month}.{date.year}'   
        if self.radioButton_2.isChecked():
            self.mode = 'doi'
        elif self.radioButton.isChecked():
            self.mode = 'name'
        self.id = self.lineEdit_3.text()
        if not self.id:
            self.id = 1
        if not self.target_dir:
            self.target_dir = '.'
        self.object = pars(self.filepath, self.id, self.name, self.date, self.mode, self.names, self.target_dir)
        print(self.name, self.date, self.id, self.target_dir, self.filepath, self.names)
        if self.checkinit():
            self.pushButton.setEnabled(False)
            self.Search()
          
    def checkinit(self):
        try:
            assert self.filepath != None or self.names != []
        except AssertionError:
            t = QtWidgets.QMessageBox()
            t.setIcon(QtWidgets.QMessageBox.Critical)
            t.setText('Error')
            t.setInformativeText('Введите данные')
            t.setWindowTitle('Error')
            t.exec_()
            return 0
        try:
            assert ((self.filepath != None) and (self.names == [])) or ((self.filepath == None) and (self.names != []))
        except AssertionError:
            t = QtWidgets.QMessageBox()
            t.setIcon(QtWidgets.QMessageBox.Critical)
            t.setText('Error')
            t.setInformativeText('Можно воспользоваться только одним способом ввода запроса')
            t.setWindowTitle('Error')
            t.exec_()
            return 0
        try:
            assert self.mode is not None
        except AssertionError:
            t = QtWidgets.QMessageBox()
            t.setIcon(QtWidgets.QMessageBox.Critical)
            t.setText('Error')
            t.setInformativeText('Выберите один из типов поиска')
            t.setWindowTitle('Error')
            t.exec_()
            return 0
        try:
            assert os.path.isdir(self.target_dir)
        except AssertionError:
            t = QtWidgets.QMessageBox()
            t.setIcon(QtWidgets.QMessageBox.Critical)
            t.setText('Error')
            t.setInformativeText('В качестве целевого пути необходимо указать папку а не файл')
            t.setWindowTitle('Error')
            t.exec_()
            return 0
        try:
            assert self.filepath==  None or ((os.path.isfile(self.filepath)) and (self.filepath[-4:] == '.txt'))
        except AssertionError:
            t = QtWidgets.QMessageBox()
            t.setIcon(QtWidgets.QMessageBox.Critical)
            t.setText('Error')
            t.setInformativeText('В качестве источника нужно указать файл .txt')
            t.setWindowTitle('Error')
            t.exec_()
            return 0
        return 1
        


    def Search(self):
        self.reportProgress("Поиск запускается...")
        self.thread = QtCore.QThread()
        self.worker = WorkerThread(self.object)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.output.textWritten.connect(self.reportProgress)
        self.worker.finished.connect(self.reportFinished)
       
        #self.pushButton_6.clicked.connect(self.sendval)
        #self.lineEdit_5.returnPressed.connect(self.sendval)

        self.thread.start()
        # добавить прокручивание окна textBrowser_4
        
    def sendval(self):
        val = self.lineEdit_5.text()
        if self.worker.running == True:
            if val:
                self.worker.input.text = val
                self.lineEdit_5.clear()

                self.textBrowser_4.insertPlainText(val)
                cond.wakeAll()
            else:
                self.textBrowser_4.insertPlainText('Пожалуйста, введите число\n')
        
        
    def reportFinished(self):
        self.textBrowser_4.insertPlainText('Поиск завершен\n')
        self.pushButton.setEnabled(True)
        
    def reportProgress(self, n):

        self.textBrowser_4.insertPlainText(n + '\n')
        self.textBrowser_4.moveCursor(QtGui.QTextCursor.End)
        self.textBrowser_4.ensureCursorVisible()
        
class pars:
    def __init__(self, filepath, ID, name, date, mode, names, target):
        self.filepath = filepath
        self.id = ID
        self.name = name
        self.date = date
        self.mode = mode
        self.names = names
        self.target = target

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Activity()
    ui.setupUi(Dialog)
    ui.pushButton_5.clicked.connect(partial(ui.push_the_button_search, 2))
    ui.pushButton_3.clicked.connect(partial(ui.push_the_button_search,1))
    ui.pushButton_2.clicked.connect(ui.push_the_button_add)
    ui.pushButton_4.clicked.connect(ui.push_the_button_delete)
    ui.pushButton.clicked.connect(ui.Compose)
    Dialog.show()
    sys.exit(app.exec())
