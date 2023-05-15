from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, \
    QLineEdit, QGridLayout, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, \
    QVBoxLayout, QComboBox, QToolBar, QStatusBar, QMessageBox

from PyQt6.QtCore import Qt

from PyQt6.QtGui import QAction, QIcon, QFont
import sys
import sqlite3
import mysql.connector


def check(phone):
    if not phone.isdigit():
        return False
    if not len(phone) == 10:
        return False
    return True


class DatabaseConnection:
    def __init__(self, host="localhost", user="root", password="metathedata@99", database="school"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        connection = mysql.connector.connect(host=self.host, user=self.user,
                                             password=self.password, database=self.database)
        return connection


# QMainWindow allows to add MENUBAR, HELPBAR, and STATUSBAR - better layout options

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(600, 600)
        # Creating menu items
        file_menu_item = self.menuBar().addMenu("&File")  # Due to convention you need to put & symbol first
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")

        # Creating sub-menu items
        add_student_action = QAction(QIcon("icons/add.png"), "Add Student",
                                     self)  # Added self - to connect it actual current class
        add_student_action.triggered.connect(self.insert_student_window)
        file_menu_item.addAction(add_student_action)

        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.triggered.connect(self.insert_about_dialog)

        search_action = QAction(QIcon("icons/search.png"), "Search", self)
        search_action.triggered.connect(self.insert_search_window)
        edit_menu_item.addAction(search_action)

        # help_action = QAction("Help")
        # help_menu_item.addAction(help_action)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # Create toolbar and add toolbar elements
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)

        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # Create status bar and add status bar elements
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Detect a cell click
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        btn_edit = QPushButton("Edit Record")
        btn_edit.clicked.connect(self.insert_edit_window)

        btn_delete = QPushButton("Delete Record")
        btn_delete.clicked.connect(self.insert_delete_window)

        # To prevent Duplications
        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget(btn_edit)
        self.statusbar.addWidget(btn_delete)

    def load_data(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students")
        result = cursor.fetchall()
        self.table.setRowCount(0)  # Resets the row count to 0 so after restart data does not gets appended
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_num, data in enumerate(row_data):
                self.table.setItem(row_number, column_num, QTableWidgetItem(str(data)))

        connection.close()

    def insert_student_window(self):
        dialog = AddStudentDialog()
        dialog.exec()

    def insert_search_window(self):
        dialog = SearchStudentDialog()
        dialog.exec()

    def insert_edit_window(self):
        dialog = EditDialog()
        dialog.exec()

    def insert_delete_window(self):
        dialog = DeleteDialog()
        dialog.exec()

    def insert_about_dialog(self):
        dialog = AboutDialog()
        dialog.exec()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")

        content = """
Introducing the student record program created by Aarsh Patel using Python and PYQT6 libraries. This user-friendly program allows you to easily manage and keep track of student information such as names, IDs, grades, and other relevant data.

With its intuitive interface, the program enables you to add, edit, and delete student records effortlessly. The data is stored in a secure database, ensuring that it is always available when you need it.

Aarsh Patel's student record program also provides a search function that allows you to quickly find specific student records by entering keywords or phrases. You can also sort the data by different criteria such as name, ID, or grade.

Whether you're a teacher, administrator, or student, this program is a valuable tool for managing student information efficiently. Thanks to Aarsh Patel's expertise in Python and PYQT6 libraries, this program is reliable, user-friendly, and efficient.
        
Feel free to use and modify the code to your use.
        """

        self.setText(content)


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Record")
        # self.setFixedWidth(300)
        # self.setFixedHeight(150)

        # Getting current Student details:
        index = main_window.table.currentRow()  # Selected row
        self.stu_id = main_window.table.item(index, 0).text()

        layout = QGridLayout()

        confirmation = QLabel("Are you sure you want to delete this record?")
        # confirmation.font().setBold(True)
        btn_yes = QPushButton("Yes")
        btn_no = QPushButton("No")

        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(btn_yes, 1, 0)
        layout.addWidget(btn_no, 1, 1)
        self.setLayout(layout)

        btn_yes.clicked.connect(self.delete_student_record)
        btn_no.clicked.connect(self.close)

    def delete_student_record(self):
        index = main_window.table.currentRow()  # Selected row
        id = main_window.table.item(index, 0).text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE from students WHERE id = %s", (id,))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()

        self.close()

        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The record was deleted successfully!")
        confirmation_widget.exec()


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student Record")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Getting current Student details:
        index = main_window.table.currentRow()  # Selected row
        self.stu_id = main_window.table.item(index, 0).text()
        stu_name = main_window.table.item(index, 1).text()
        stu_course = main_window.table.item(index, 2).text()
        stu_phone = main_window.table.item(index, 3).text()

        # create Widgets
        self.student_name = QLineEdit(stu_name)
        self.student_name.setPlaceholderText("Name")

        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(stu_course)

        self.phone = QLineEdit(stu_phone)
        self.phone.setPlaceholderText("Phone")

        btn_update = QPushButton("UPDATE")
        btn_update.clicked.connect(self.edit_record)



        # Add Widgets to layout
        layout.addWidget(self.student_name)
        layout.addWidget(self.course_name)
        layout.addWidget(self.phone)
        layout.addWidget(btn_update)


        self.setLayout(layout)

    def edit_record(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        name = self.student_name.text()
        course = self.course_name.currentText()
        phone = self.phone.text()
        if check(phone):
            id = self.stu_id
            cursor.execute("UPDATE students SET name=%s, course=%s, mobile=%s WHERE id= %s",
                           (name, course, phone, id))
            connection.commit()
            cursor.close()
            connection.close()

            # To Refresh the table data
            main_window.load_data()

            message_widget = QMessageBox()
            message_widget.setWindowTitle("Cell Edited")
            message_widget.setText("Cell Successfully edited !")
            message_widget.exec()

            self.close()
        else:
            error_widget = QMessageBox()
            error_widget.setWindowTitle("Error : Invalid input")
            error_widget.setText("Please enter a 10 digit phone number!")
            error_widget.exec()



class AddStudentDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Student Record")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # create Widgets
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")

        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)

        self.phone = QLineEdit()
        self.phone.setPlaceholderText("Phone")

        btn_register = QPushButton("Register")
        btn_register.clicked.connect(self.add_student)

        # self.notification_label = QLabel("")
        # # self.notification_label.setFont(QFont("Arial", 5))
        # #self.notification_label.setStyleSheet("QLabel { color : blue; }")

        # Add Widgets to layout
        layout.addWidget(self.student_name)
        layout.addWidget(self.course_name)
        layout.addWidget(self.phone)
        layout.addWidget(btn_register)
        # layout.addWidget(self.notification_label)

        self.setLayout(layout)

    def add_student(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        name = self.student_name.text()
        course = self.course_name.currentText()
        phone = self.phone.text()
        if check(phone):
            cursor.execute("INSERT INTO students (name, course, mobile) VALUES(%s,%s,%s)",
                           (name, course, phone))
            connection.commit()
            cursor.close()
            connection.close()

            # To Refresh the table data
            main_window.load_data()
            self.student_name.clear()
            self.course_name.setCurrentText("Biology")
            self.phone.clear()

            # self.notification_label.setText("Successfully Added !")

        else:
            error_widget = QMessageBox()
            error_widget.setWindowTitle("Error : Invalid input")
            error_widget.setText("Please enter a 10 digit phone number!")
            error_widget.exec()
            self.phone.clear()


class SearchStudentDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # create Widgets
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")

        btn_search = QPushButton("Search")
        btn_search.clicked.connect(self.do_search)

        # Add Widgets to layout
        layout.addWidget(self.student_name)
        layout.addWidget(btn_search)
        self.setLayout(layout)

    def do_search(self):
        name = self.student_name.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students WHERE name = %s", (name,))
        result = cursor.fetchall()
        # Tuple can't be left with just one member it has to be member and a comma
        rows = list(result)
        # print(rows)
        items = main_window.table.findItems(name,
                                            Qt.MatchFlag.MatchFixedString)
        for item in items:
            # print(item)
            main_window.table.item(
                item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())
