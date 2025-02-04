# User-Interface to automatically acquire the data from the HSI camera and extract the physiological parameters

## Introduction
 This project focuses on developing a **Graphical User Interface (GUI)** for **automatic transfer and visualization** of **Hyperspectral Imaging (HSI) cubes**


### **Project Goals**  
The main objectives of this project are:    
- **Develop a GUI** to visualize and analyze HSI data.  
- **Calculate and display a boundary line** based on  tissue hemoglobin index parameter.  

---

## **Features**  
The GUI will integrate the following functionalities:  

1. **Load HSI Cube & Display RGB Image**  
   - Convert HSI cube into an RGB image.  
   - Display the image within the GUI.  

2. **Mark Two Regions of Interest (ROIs)**  
   - **ROI1**: A central non-critical area (marked freehand or using a marker).  
   - **ROI2**: A larger area covering the region under investigation.  

3. **Calculate the Boundary Line**  
   - Compute the **Median Tissue Hemoglobin Index (mTHI1)** of ROI1.  
   - Calculate pixel-wise differences relative to mTHI1 for ROI2.  
   - Apply a threshold to classify pixels as **inside or outside** the boundary.  

4. **Save & Display the Processed Image**  
   - Generate a **binary mask** based on thresholding.  
   - Overlay the **boundary line** onto the image.  
   - Save the processed image for further analysis.  

---


## **Technical Implementation**  

### **Data Processing Steps**  
  
- **Calculate the RGB image** from HSI data.  
- **Mark ROIs** using drawing tools (freehand or marker).  
- **Compute mTHI1 for ROI1** and **calculate pixel differences** in ROI2.  
- **Thresholding**: Classify pixels as **inside** or **outside** the boundary.  
- **Overlay boundary line** on the image and save the result.  

### **Technology Stack**  
- **Programming Language**: Python  
- **GUI Framework**: PyQt / Tkinter / OpenCV  
- **Data Processing**: NumPy, SciPy  
- **Image Handling**: OpenCV, Matplotlib  



## Installation
To set up the project on your local machine, follow these steps:

1. Clone the repository:
   ```sh
   git clone https://github.com/sahadvillan/HSI_GUI.git
   ```

2. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage
To run the project, use the following command:
```sh
python main.py
```

Make sure all dependencies are installed before executing the script.



## Authors
     - Sahad Muhammed Villan





