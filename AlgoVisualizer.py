from PyQt6.QtCore import Qt, pyqtSignal, QRectF, QTimer, QObject, QPointF, QSizeF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QComboBox, QLabel, QLineEdit, QSpinBox, QSlider,
                             QTabWidget, QTextEdit, QPlainTextEdit, QListWidget)
import sys
import re

class AnimatedRect(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        self.color = QColor(100, 200, 255)
        self.position = QPointF(0, 0)
        self.size = QSizeF(0, 0)
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.animation_step)
        self.animation_steps = []
        self.current_step = 0

    def set_color(self, color):
        self.color = color

    def set_value(self, value):
        self.value = value

    def set_position(self, position):
        self.position = position

    def set_size(self, size):
        self.size = size

    def start_animation(self, target_position, target_color):
        self.animation_steps = [
            (self.position, self.color),
            (target_position, target_color),
            (self.position, self.color)
        ]
        self.current_step = 0
        self.animation_timer.start(50)  # 20 fps

    def animation_step(self):
        if self.current_step < len(self.animation_steps) - 1:
            start = self.animation_steps[self.current_step]
            end = self.animation_steps[self.current_step + 1]
            t = 0.1  # Interpolation factor
            self.position = start[0] * (1-t) + end[0] * t
            self.color = QColor(
                int(start[1].red() * (1-t) + end[1].red() * t),
                int(start[1].green() * (1-t) + end[1].green() * t),
                int(start[1].blue() * (1-t) + end[1].blue() * t)
            )
            self.current_step += 1
        else:
            self.animation_timer.stop()

class VisualizerWidget(QWidget): #updated
    def __init__(self, tracked_array):
        super().__init__()
        self.tracked_array = tracked_array
        self.setMinimumSize(600, 400)
        self.zoom_factor = 1.0
        self.rectangles = []

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.scale(self.zoom_factor, self.zoom_factor)

        for rect in self.rectangles:
            painter.setBrush(QBrush(rect.color))
            painter.setPen(QPen(Qt.GlobalColor.black, 2))
            painter.drawRect(QRectF(rect.position, rect.size))
            painter.drawText(QRectF(rect.position, rect.size),
                             Qt.AlignmentFlag.AlignCenter, str(rect.value))

    def update_visualization(self):
        self.rectangles.clear()
        if not self.tracked_array.elements:
            self.update()
            return
        element_width = min(80, (self.width() - 20) / len(self.tracked_array.elements))
        element_height = 40
        start_x = (self.width() - element_width * len(self.tracked_array.elements)) / 2
        start_y = self.height() / 2 - element_height / 2

        for i, value in enumerate(self.tracked_array.elements):
            rect = AnimatedRect(self)
            rect.set_value(value)
            rect.set_position(QPointF(start_x + i * element_width, start_y))
            rect.set_size(QSizeF(element_width, element_height))
            self.rectangles.append(rect)

        self.update()

    def animate_change(self, index, new_value):
        if 0 <= index < len(self.rectangles):
            rect = self.rectangles[index]
            rect.set_value(new_value)
            current_pos = rect.position
            target_pos = QPointF(current_pos.x(), current_pos.y() - 20)
            rect.start_animation(target_pos, QColor(255, 100, 100))
            QTimer.singleShot(1000, lambda: self.update())

    def set_zoom(self, zoom_factor):
        self.zoom_factor = zoom_factor / 100.0
        self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_visualization()

class DataStructure:
    def __init__(self):
        self.elements = []

    def insert(self, value):
        self.elements.append(value)

    def remove(self, value):
        if value in self.elements:
            self.elements.remove(value)

    def search(self, value):
        return value in self.elements

class BinarySearchTree(DataStructure):
    def insert(self, value):
        if not self.elements:
            self.elements.append(value)
        else:
            self._insert_recursive(value, 0)

    def _insert_recursive(self, value, index):
        if index >= len(self.elements):
            self.elements.extend([None] * (index - len(self.elements) + 1))
            self.elements[index] = value
            return

        if self.elements[index] is None:
            self.elements[index] = value
            return

        if value < self.elements[index]:
            self._insert_recursive(value, 2 * index + 1)
        else:
            self._insert_recursive(value, 2 * index + 2)

class HashMap(DataStructure):
    def __init__(self, size=10):
        super().__init__()
        self.size = size
        self.elements = [[] for _ in range(size)]

    def insert(self, key, value):
        hash_key = hash(key) % self.size
        for item in self.elements[hash_key]:
            if item[0] == key:
                item[1] = value
                return
        self.elements[hash_key].append([key, value])

    def search(self, key):
        hash_key = hash(key) % self.size
        for item in self.elements[hash_key]:
            if item[0] == key:
                return item[1]
        return None

class TrackedArray:
    def __init__(self, initial_array=None):
        self.elements = initial_array if initial_array is not None else []
        self.history = [("initial", self.elements.copy())]

    def insert(self, value):
        self.elements.append(value)
        self.history.append(("insert", value))

    def remove(self, value):
        if value in self.elements:
            index = self.elements.index(value)
            self.elements.remove(value)
            self.history.append(("remove", index))

    def update(self, index, value):
        if 0 <= index < len(self.elements):
            old_value = self.elements[index]
            self.elements[index] = value
            self.history.append(("update", index, old_value, value))

class ControlPanel(QWidget):
    insert_signal = pyqtSignal(str)
    remove_signal = pyqtSignal(str)
    update_signal = pyqtSignal(int, str)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.value_input = QLineEdit()
        layout.addWidget(QLabel("Value:"))
        layout.addWidget(self.value_input)

        self.index_input = QSpinBox()
        self.index_input.setMinimum(0)
        layout.addWidget(QLabel("Index:"))
        layout.addWidget(self.index_input)

        insert_button = QPushButton("Insert")
        insert_button.clicked.connect(lambda: self.insert_signal.emit(self.value_input.text()))
        layout.addWidget(insert_button)

        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(lambda: self.remove_signal.emit(self.value_input.text()))
        layout.addWidget(remove_button)

        update_button = QPushButton("Update")
        update_button.clicked.connect(lambda: self.update_signal.emit(self.index_input.value(), self.value_input.text()))
        layout.addWidget(update_button)

        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(50, 200)
        self.zoom_slider.setValue(100)
        layout.addWidget(QLabel("Zoom"))
        layout.addWidget(self.zoom_slider)

        self.setLayout(layout)

class HistoryWidget(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)

    def update_history(self, history):
        self.clear()
        for action in history:
            if action[0] == "initial":
                self.append(f"Initial array: {action[1]}")
            elif action[0] == "insert":
                self.append(f"Inserted: {action[1]}")
            elif action[0] == "remove":
                self.append(f"Removed at index: {action[1]}")
            elif action[0] == "update":
                self.append(f"Updated index {action[1]}: {action[2]} -> {action[3]}")

class LoopVisualizerWidget(QWidget):
    run_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()

        self.code_input = QPlainTextEdit()
        self.code_input.setPlaceholderText("Enter your loop or operations here. Example:\n"
                                           "for i in range(len(arr)):\n"
                                           "    arr[i] = arr[i] * 2")
        layout.addWidget(self.code_input)

        self.run_button = QPushButton("Run Visualization")
        self.run_button.clicked.connect(lambda: self.run_signal.emit(self.code_input.toPlainText()))
        layout.addWidget(self.run_button)

        self.array_view = QTextEdit()
        self.array_view.setReadOnly(True)
        layout.addWidget(self.array_view)

        self.setLayout(layout)

    def update_array_view(self, array):
        self.array_view.setText(f"Current Array: {array}")

class MainWindow(QMainWindow):
    def __init__(self, initial_array=None):
        super().__init__()
        self.setWindowTitle("Advanced Algorithm Visualizer")
        self.setGeometry(100, 100, 1200, 800)

        main_widget = QWidget()
        main_layout = QHBoxLayout()

        self.tracked_array = TrackedArray(initial_array if initial_array else [])
        self.visualizer = VisualizerWidget(self.tracked_array)
        main_layout.addWidget(self.visualizer, 7)

        right_panel = QTabWidget()

        # Control Panel Tab
        control_tab = QWidget()
        control_layout = QVBoxLayout()
        self.control_panel = ControlPanel()
        self.control_panel.insert_signal.connect(self.insert_element)
        self.control_panel.remove_signal.connect(self.remove_element)
        self.control_panel.update_signal.connect(self.update_element)
        self.control_panel.zoom_slider.valueChanged.connect(self.visualizer.set_zoom)
        control_layout.addWidget(self.control_panel)
        self.history_widget = HistoryWidget()
        control_layout.addWidget(self.history_widget)
        control_tab.setLayout(control_layout)
        right_panel.addTab(control_tab, "Control Panel")

        # Loop Visualizer Tab
        self.loop_visualizer = LoopVisualizerWidget()
        self.loop_visualizer.run_signal.connect(self.run_loop_visualization)
        right_panel.addTab(self.loop_visualizer, "Loop Visualizer")

        # Array History Tab
        self.array_history_widget = QListWidget()
        right_panel.addTab(self.array_history_widget, "Array History")

        main_layout.addWidget(right_panel, 3)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.animation_step)
        self.animation_steps = []

        self.update_visualization()

    def update_visualization(self):
        self.visualizer.update_visualization()
        self.history_widget.update_history(self.tracked_array.history)
        self.loop_visualizer.update_array_view(self.tracked_array.elements)
        self.update_array_history()
        QApplication.processEvents()
    
    def insert_element(self, value):
        try:
            self.tracked_array.insert(int(value))
            self.update_visualization()
        except ValueError:
            print("Invalid input")

    def remove_element(self, value):
        try:
            self.tracked_array.remove(int(value))
            self.update_visualization()
        except ValueError:
            print("Invalid input or element not found")

    def update_element(self, index, value):
        try:
            self.tracked_array.update(index, int(value))
            self.update_visualization()
        except ValueError:
            print("Invalid input")

    def update_array_history(self):
        self.array_history_widget.addItem(f"State {self.array_history_widget.count() + 1}: {self.tracked_array.elements}")

    def run_loop_visualization(self, code):
        # Reset animation steps
        self.animation_steps = []
        
        # Create a copy of the current array for manipulation
        temp_array = self.tracked_array.elements.copy()
        
        # Create a safe local environment for code execution
        local_env = {'arr': temp_array}
        
        try:
            # Execute the code
            exec(code, {}, local_env)
            
            # Capture the final state of the array
            final_array = local_env['arr']
            
            # Generate animation steps
            for i, (old, new) in enumerate(zip(self.tracked_array.elements, final_array)):
                if old != new:
                    self.animation_steps.append((i, new))
            
            # If there are changes, start the animation
            if self.animation_steps:
                self.animation_timer.start(1000)  # 1 second between steps
            else:
                print("No changes detected in the array.")
        except Exception as e:
            print(f"Error executing code: {e}")

    def animation_step(self):
        if self.animation_steps:
            index, value = self.animation_steps.pop(0)
            self.tracked_array.update(index, value)
            self.visualizer.animate_change(index, value)
            QTimer.singleShot(1000, self.update_visualization)
        else:
            self.animation_timer.stop()


def run_visualizer(initial_array=None):
    app = QApplication(sys.argv)
    main_window = MainWindow(initial_array)
    main_window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    run_visualizer()