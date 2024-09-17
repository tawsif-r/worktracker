import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QListWidget, QLabel
from PyQt5.QtCore import QTimer, Qt
import sqlite3
from datetime import datetime, timedelta

class WorkTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Work Tracker")
        self.setGeometry(100, 100, 400, 500)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.timer_label = QLabel("00:00:00")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("font-size: 24px;")
        self.layout.addWidget(self.timer_label)

        self.button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.pause_button = QPushButton("Pause")
        self.stop_button = QPushButton("Stop")
        self.button_layout.addWidget(self.start_button)
        self.button_layout.addWidget(self.pause_button)
        self.button_layout.addWidget(self.stop_button)
        self.layout.addLayout(self.button_layout)

        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Enter task description")
        self.layout.addWidget(self.task_input)

        self.task_list = QListWidget()
        self.layout.addWidget(self.task_list)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.elapsed_time = timedelta()
        self.is_running = False

        self.start_button.clicked.connect(self.start_timer)
        self.pause_button.clicked.connect(self.pause_timer)
        self.stop_button.clicked.connect(self.stop_timer)

        self.init_db()
        self.load_tasks()

    def init_db(self):
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'worktracker.db')
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS tasks
                               (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                description TEXT,
                                duration INTEGER,
                                date TEXT)''')
        self.conn.commit()

    def load_tasks(self):
        self.cursor.execute("SELECT description, duration, date FROM tasks ORDER BY date DESC LIMIT 10")
        tasks = self.cursor.fetchall()
        for task in tasks:
            description, duration, date = task
            duration = timedelta(seconds=duration)
            self.task_list.addItem(f"{description} - {duration} - {date}")

    def update_timer(self):
        self.elapsed_time += timedelta(seconds=1)
        self.timer_label.setText(str(self.elapsed_time).split('.')[0])

    def start_timer(self):
        if not self.is_running:
            self.timer.start(1000)
            self.is_running = True

    def pause_timer(self):
        if self.is_running:
            self.timer.stop()
            self.is_running = False

    def stop_timer(self):
        self.timer.stop()
        self.is_running = False
        self.save_task()
        self.elapsed_time = timedelta()
        self.timer_label.setText("00:00:00")

    def save_task(self):
        description = self.task_input.text()
        duration = self.elapsed_time.total_seconds()
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.cursor.execute("INSERT INTO tasks (description, duration, date) VALUES (?, ?, ?)",
                            (description, duration, date))
        self.conn.commit()

        self.task_list.insertItem(0, f"{description} - {self.elapsed_time} - {date}")
        self.task_input.clear()

def main():
    app = QApplication(sys.argv)
    tracker = WorkTracker()
    tracker.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()