import sys
import webbrowser
from PyQt5 import QtWidgets ,QtCore

class HTMLViewer(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("HTML Viewer")
        self.setGeometry(100, 100, 200, 100)

        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QtWidgets.QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.button = QtWidgets.QPushButton("Open HTML File")
        self.button.clicked.connect(self.open_html_file)
        self.layout.addWidget(self.button)

    def open_html_file(self):
        file_name = "shortest-path.html"
        file_path = QtCore.QDir.current().filePath(file_name)
        webbrowser.open(file_path)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    viewer = HTMLViewer()
    viewer.show()
    sys.exit(app.exec_())
