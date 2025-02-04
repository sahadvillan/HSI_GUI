import sys
import numpy as np
import cv2
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QLineEdit, QFileDialog, QMessageBox, QFrame)  # Add QFrame here
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


# Add QFrame to your imports if not already imported
from PyQt5.QtWidgets import QFrame

class ROIAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        #self.setWindowTitle("THI")
        self.setGeometry(90, 90, 1000, 600)

        # Main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        # Create a horizontal layout for splitting the screen into left and right sections
        self.layout = QHBoxLayout(self.main_widget)

        # Create the left section (for the canvas)
        self.left_layout = QVBoxLayout()
        self.layout.addLayout(self.left_layout)

        # Create the right section (for buttons, lineedit, and label)
        self.right_layout = QVBoxLayout()
        self.layout.addLayout(self.right_layout)

        # Apply styles for the entire widget
        self.setStyleSheet("""
        QWidget {
            background-color: black;
        }
        QFrame, QLabel, QToolTip {
            border: 2px solid grey;
            border-radius: 4px;
            padding: 2px;
            background-color: rgb(0, 0, 0);
            color: #ffffff;  /* Ensures text is visible on the dark background */
        }
        QPushButton {
            border: 2px solid rgb(44, 62, 80);
            border-radius: 20px;
            color: #ffffff;
            background-color: rgb(0, 0, 0);
        }
        QPushButton:focus {
            border: 2px solid rgb(85, 170, 255);
            background-color: rgb(43, 45, 56);
        }
        
        QLineEdit {
            border: 2px solid grey;
            border-radius: 4px;
            padding: 4px;
            background-color: rgb(20, 20, 20);
            color: white;  /* Set text color to white */
        }
        """)

        # Define button style for consistent use
        button_stylesheet = """
        QPushButton {
            border: 2px solid rgb(44, 62, 80);
            border-radius: 20px;
            color: #ffffff;
            background-color: rgb(0, 0, 0);
        }
        QPushButton:focus {
            border: 2px solid rgb(85, 170, 255);
            background-color: rgb(43, 45, 56);
        }
        """

        # UI Elements for the right section


        # Create a horizontal layout for the threshold label and lineedit
        self.threshold_layout = QHBoxLayout()

        self.threshold_label = QLabel("Threshold:", self)
        self.threshold_layout.addWidget(self.threshold_label)

        self.threshold_entry = QLineEdit(self)
        self.threshold_entry.setText("0.1")
        self.threshold_layout.addWidget(self.threshold_entry)

        # Add the horizontal layout to the right layout
        self.right_layout.addLayout(self.threshold_layout)

        self.calculate_button = QPushButton("Draw Boundary Line", self)
        self.calculate_button.setStyleSheet(button_stylesheet)
        self.calculate_button.clicked.connect(self.calculate)
        self.calculate_button.setMinimumSize(241, 101)
        self.right_layout.addWidget(self.calculate_button)


# Add the "Mark Two Regions" button
        self.mark_two_regions_button = QPushButton("Mark Two Regions", self)
        self.mark_two_regions_button.setStyleSheet(button_stylesheet)
        self.mark_two_regions_button.clicked.connect(self.start_marking_two_regions)
        self.mark_two_regions_button.setMinimumSize(241, 101)
        self.right_layout.addWidget(self.mark_two_regions_button)





        self.save_button = QPushButton("Save Image", self)
        self.save_button.setStyleSheet(button_stylesheet)
        self.save_button.clicked.connect(self.save_image)
        self.save_button.setMinimumSize(241, 101)
        self.right_layout.addWidget(self.save_button)


        self.load_button = QPushButton("Load HSI", self)
        self.load_button.setStyleSheet(button_stylesheet)
        self.load_button.clicked.connect(self.load_image)
        self.load_button.setMinimumSize(241, 101)
        self.right_layout.addWidget(self.load_button)


        # Matplotlib Figure and Canvas (for the left section)
        self.fig = Figure(figsize=(9, 6), facecolor='black')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('black')
        self.ax.axis('off')

        # Create a QFrame to add a grey border around the figure
        self.frame = QFrame(self.main_widget)
        self.frame.setStyleSheet("QFrame { border: 2px solid grey; border-radius: 4px; padding: 4px; }")

        # Set the canvas as the central widget of the frame
        self.canvas = FigureCanvas(self.fig)
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.addWidget(self.canvas)

        # Add the frame to the left layout
        self.left_layout.addWidget(self.frame)

        # Initialize variables
        self.image = None
        self.rgb_image = None
        self.thi_image = None
        self.roi1 = None
        self.mthi1 = None
        self.binary_mask = None
        self.current_roi = []
        self.drawing = False
        self.roi2 = None  # Second ROI
        self.current_roi_index = 0  # 0 for ROI1, 1 for ROI2
        # Connect mouse events
        self.canvas.mpl_connect("button_press_event", self.start_draw)
        self.canvas.mpl_connect("motion_notify_event", self.draw)
        self.canvas.mpl_connect("button_release_event", self.end_draw)



    def load_image(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Dat Files (*.dat)")
        if not filepath:
            return

        self.image = self.read_cube_dat(filepath)
        self.rgb_image = self.image[:, :, [29, 19, 9]]  # Example bands for RGB
        self.thi_image = self.calc_thi(self.image)
        self.rgb_image = np.rot90(self.rgb_image)
        self.ax.clear()

        self.ax.imshow(self.rgb_image)
        self.ax.set_facecolor('black')
        self.ax.axis('off')
        self.ax.set_title("RGB Image")
        self.canvas.draw()

        self.thi_image = np.rot90(self.thi_image)

    def read_cube_dat(self, filenamecube):
        cube_shape = np.fromfile(filenamecube, dtype='>i', count=3)
        height = cube_shape[1]
        width = cube_shape[0]
        channels = cube_shape[2]

        data = np.fromfile(filenamecube, dtype='>f')
        data_cube = data[3:].reshape(width, height, channels)
        return data_cube

    def calc_thi(self, cube, minWL=500, maxWL=995, WLsteps=5):
        a = 0.4
        b = 1.55
        first_range_start = int((530 - minWL) / WLsteps)
        first_range_end = int((585 - minWL) / WLsteps) + 1
        second_range_start = int((785 - minWL) / WLsteps)
        second_range_end = int((820 - minWL) / WLsteps) + 1

        mean_value1 = cube[:, :, first_range_start:first_range_end].mean(axis=2)
        mean_value2 = cube[:, :, second_range_start:second_range_end].mean(axis=2)

        thi_image = (-np.log(mean_value1 / mean_value2) - a) / (b - a)
        np.clip(thi_image, 0.000001, 1, out=thi_image)
        return thi_image




    def start_draw(self, event):
        if event.inaxes != self.ax:
            return
        self.drawing = True
        if self.current_roi_index == 0:
            self.current_roi = [(event.xdata, event.ydata)]
        else:
            self.current_roi = [(event.xdata, event.ydata)]

    def draw(self, event):
        if not self.drawing or event.inaxes != self.ax:
            return
        self.current_roi.append((event.xdata, event.ydata))

        self.ax.clear()
        self.ax.set_facecolor('black')
        self.ax.axis('off')
        self.ax.imshow(self.rgb_image)

        if self.roi1 is not None:
            self.ax.plot(self.roi1[:, 0], self.roi1[:, 1], 'r-', label="ROI1")

        if self.roi2 is not None:
            self.ax.plot(self.roi2[:, 0], self.roi2[:, 1], 'b-', label="ROI2")

        self.ax.plot([p[0] for p in self.current_roi], [p[1] for p in self.current_roi], 'g-', label="Current ROI")
        self.canvas.draw()

    def end_draw(self, event):
        if not self.drawing or event.inaxes != self.ax:
            return
        self.drawing = False
        self.current_roi.append((event.xdata, event.ydata))

        if self.current_roi_index == 0:
            self.roi1 = np.array(self.current_roi)
            self.current_roi_index = 1  # Switch to ROI2
        else:
            self.roi2 = np.array(self.current_roi)
            self.current_roi_index = 0  # Switch back to ROI1

        self.ax.clear()
        self.ax.set_facecolor('black')
        self.ax.axis('off')
        self.ax.imshow(self.rgb_image)

        if self.roi1 is not None:
            self.ax.plot(self.roi1[:, 0], self.roi1[:, 1], 'r-', label="ROI1")

        if self.roi2 is not None:
            self.ax.plot(self.roi2[:, 0], self.roi2[:, 1], 'b-', label="ROI2")

        self.canvas.draw()
    def calculate(self):
        if self.roi1 is None or self.roi2 is None or self.thi_image is None:
            QMessageBox.warning(self, "Error", "Please load an image and mark two regions first.")
            return

        # Calculate mTHI1 and mTHI2
        roi1_mask = self.create_mask(self.roi1)
        roi2_mask = self.create_mask(self.roi2)

        mthi1_values = self.thi_image[roi1_mask == 1]  # Use only pixels inside the mask for ROI1
        mthi2_values = self.thi_image[roi2_mask == 1]  # Use only pixels inside the mask for ROI2

        self.mthi1 = np.median(mthi1_values)
        self.mthi2 = np.median(mthi2_values)

        print(f"Median THI for ROI1: {self.mthi1}")
        print(f"Median THI for ROI2: {self.mthi2}")

        # Calculate binary mask based on the difference between ROI1 and ROI2
        threshold = float(self.threshold_entry.text())
        diff = self.thi_image - self.mthi1
        self.binary_mask = (diff >= threshold)

        # Display the boundary
        boundary = cv2.Canny(self.binary_mask.astype(np.uint8) * 255, 100, 200)
        self.ax.clear()
        self.ax.imshow(self.rgb_image)
        self.ax.imshow(self.binary_mask, cmap='gray', alpha=0.5)
        self.ax.contour(boundary, colors='red', linewidths=0.5)
        self.ax.set_title("Binary Mask with Boundary")
        self.ax.set_facecolor('black')
        self.ax.axis('off')
        self.canvas.draw()

        # After drawing the plot, you can get the axis dimensions
        bbox = self.ax.get_window_extent()
        print(f"Axis Bounding Box (in pixels): {bbox}")
        print(f"Width: {bbox.width}, Height: {bbox.height}")


    def create_mask(self, roi):
        """
        Create a binary mask for the given ROI.
        """
        mask = np.zeros(self.thi_image.shape[:2], dtype=np.uint8)
        roi_points = np.array(roi, dtype=np.int32).reshape((-1, 1, 2))
        cv2.fillPoly(mask, [roi_points], 1)
        return mask

    def save_image(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png)")
        if filepath:
            self.fig.savefig(filepath)

    def start_marking_two_regions(self):
        self.current_roi_index = 0  # Start with ROI1
        self.roi1 = None
        self.roi2 = None
        self.ax.clear()
        self.ax.set_facecolor('black')
        self.ax.axis('off')
        self.ax.imshow(self.rgb_image)
        self.canvas.draw()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ROIAnalyzer()
    window.show()
    sys.exit(app.exec_())
