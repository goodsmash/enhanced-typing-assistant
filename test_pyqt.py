from PyQt5.QtWidgets import QApplication, QLabel
import sys

def create_app():
    app = QApplication(sys.argv)
    label = QLabel('Hello, PyQt5!')
    return app, label

if __name__ == '__main__':
    app, label = create_app()
    label.show()
    sys.exit(app.exec_())
