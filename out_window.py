from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSlot, QTimer, QDate, Qt
from PyQt5.QtWidgets import QDialog, QMessageBox
import cv2
import face_recognition
import numpy as np
import datetime
import os
import csv
# from deepface import DeepFace
# from deepface.commons import functions, realtime, distance as dst


class Ui_OutputDialog(QDialog):
    def __init__(self):
        super(Ui_OutputDialog, self).__init__()
        loadUi("./outputwindow.ui", self)

        # Update time
        now = QDate.currentDate()
        current_date = now.toString('ddd dd MMMM yyyy')
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        self.Date_Label.setText(current_date)
        self.Time_Label.setText(current_time)

        # self.startCamera.clicked.connect(self.startVideo(0))
        self.image = None
        self.startCamera.clicked.connect(self.startDetection)
        self.capture = None
        self.state = 1
        self.checkInList = []
        self.checkOutDict = {}


    def startDetection(self):
        if self.state == 1:
            self.state = 0
            self.capture = cv2.VideoCapture(0)
            self.startCamera.setText("Stop Detection")

            self.timer = QTimer(self)  # Create Timer
            path = 'ImagesAttendance'
            if not os.path.exists(path):
                os.mkdir(path)
            # known face encoding and known face name list
            images = []
            self.class_names = []
            self.encode_list = []
            self.TimeList1 = []
            self.TimeList2 = []
            attendance_list = os.listdir(path)
            # verification = DeepFace.verify(img1_path="Obama.jpg", img2_path="obama_pic2.jpg")
            print(attendance_list)
            for cl in attendance_list:
                cur_img = cv2.imread(f'{path}/{cl}')
                images.append(cur_img)
                self.class_names.append(os.path.splitext(cl)[0])
            print("faces encoded")
            for img in images:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                boxes = face_recognition.face_locations(img)
                encodes_cur_frame = face_recognition.face_encodings(img, boxes)[0]
                # encode = face_recognition.face_encodings(img)[0]
                self.encode_list.append(encodes_cur_frame)

            self.timer.timeout.connect(self.update_frame)  # Connect timeout to the output function
            self.timer.start(5)

        else:
            self.state = 1
            self.startCamera.setText("Start Detection")





    @pyqtSlot()
    def startVideo(self, camera_name):
        """
        :param camera_name: link of camera or usb camera
        :return:
        """
        if len(camera_name) == 1:
            self.capture = cv2.VideoCapture(int(camera_name))
        else:
            self.capture = cv2.VideoCapture(camera_name)
        self.timer = QTimer(self)  # Create Timer
        path = 'ImagesAttendance'
        if not os.path.exists(path):
            os.mkdir(path)
        # known face encoding and known face name list
        images = []
        self.class_names = []
        self.encode_list = []
        self.TimeList1 = []
        self.TimeList2 = []
        attendance_list = os.listdir(path)
        # verification = DeepFace.verify(img1_path="Obama.jpg", img2_path="obama_pic2.jpg")
        print(attendance_list)
        for cl in attendance_list:
            cur_img = cv2.imread(f'{path}/{cl}')
            images.append(cur_img)
            self.class_names.append(os.path.splitext(cl)[0])
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(img)
            encodes_cur_frame = face_recognition.face_encodings(img, boxes)[0]
            # encode = face_recognition.face_encodings(img)[0]
            self.encode_list.append(encodes_cur_frame)
        self.timer.timeout.connect(self.update_frame)  # Connect timeout to the output function
        self.timer.start(10)  # emit the timeout() signal at x=40ms

    def face_rec_(self, frame, encode_list_known, class_names):
        """
        :param frame: frame from camera
        :param encode_list_known: known face encoding
        :param class_names: known face names
        :return:
        """
        # csv
        def mark_attendance(name):
            """
            :param name: detected face known or unknown one
            :return:
            """

            with open('Attendance.csv', 'a') as f:
                if (name != 'unknown'):
                    # buttonReply = QMessageBox.question(self, 'Welcome ' + name, 'Are you Checking In?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    # if buttonReply == QMessageBox.Yes:
                    date_time_string = datetime.datetime.now().strftime("%y/%m/%d %H:%M:%S")
                    if name not in self.checkInList:
                        self.checkInList.append(name)
                        f.writelines(f'\n{name},{date_time_string},In Time')
                        print(f'\n{name},{date_time_string},In Time')

                    else:
                        self.checkOutDict[name] = date_time_string
                        print(f'{name} Already noted.')
                    self.NameLabel.setText(name)



        # face recognition
        crop_img = frame[30:440, 120:470]
        faces_cur_frame = face_recognition.face_locations(crop_img)
        encodes_cur_frame = face_recognition.face_encodings(crop_img, faces_cur_frame)
        # count = 0

        # here frame is the image
        raw_img = frame.copy()


        for encodeFace, faceLoc in zip(encodes_cur_frame, faces_cur_frame):
            match = face_recognition.compare_faces(encode_list_known, encodeFace, tolerance=0.50)
            face_dis = face_recognition.face_distance(encode_list_known, encodeFace)
            name = "unknown"
            best_match_index = np.argmin(face_dis)
            if match[best_match_index]:
                self.dataPhoto.setPixmap(QPixmap(f"ImagesAttendance/{class_names[best_match_index]}.jpg"))
                self.dataPhoto.setScaledContents(True)
                print(class_names[best_match_index])
                name = class_names[best_match_index].upper()
                y1, x2, y2, x1 = faceLoc
                print(x1, x2, y1, y2)
                cv2.rectangle(frame, (150, 50), (450, 420), (0, 255, 0), 3)

            mark_attendance(name)



        return frame



    def ElapseList(self,name):
        with open('Attendance.csv', "r") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 2

            Time1 = datetime.datetime.now()
            Time2 = datetime.datetime.now()
            for row in csv_reader:
                for field in row:
                    if field in row:
                        if field == 'In Time':
                            if row[0] == name:
                                # print(f'\t ROW 0 {row[0]}  ROW 1 {row[1]} ROW2 {row[2]}.')
                                Time1 = (datetime.datetime.strptime(row[1], '%y/%m/%d %H:%M:%S'))
                                self.TimeList1.append(Time1)
                        if field == 'Out Time':
                            if row[0] == name:
                                # print(f'\t ROW 0 {row[0]}  ROW 1 {row[1]} ROW2 {row[2]}.')
                                Time2 = (datetime.datetime.strptime(row[1], '%y/%m/%d %H:%M:%S'))
                                self.TimeList2.append(Time2)
                                #print(Time2)




    def update_frame(self):
        ret, self.image = self.capture.read()

        self.displayImage(self.image, self.encode_list, self.class_names, 1)

    def displayImage(self, image, encode_list, class_names, window=1):
        """
        :param image: frame from camera
        :param encode_list: known face encoding list
        :param class_names: known face names
        :param window: number of window
        :return:
        """

        image = cv2.resize(image, (640, 480))
        # face = image[30:440, 120:470] # the cropped face
        # cv2.imshow("Face", face)
        cv2.rectangle(image, (150, 50), (450, 420), (0, 0, 255), 3)
        self.dataPhoto.clear()
        self.NameLabel.clear()
        print(image.shape)
        # cropping image


        try:
            image = self.face_rec_(image, encode_list, class_names)
        except Exception as e:
            print(e)
        qformat = QImage.Format_Indexed8
        if len(image.shape) == 3:
            if image.shape[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888
        outImage = QImage(image, image.shape[1], image.shape[0], image.strides[0], qformat)
        outImage = outImage.rgbSwapped()

        if self.state == 0:
            self.imgLabel.setPixmap(QPixmap.fromImage(outImage))
            self.imgLabel.setScaledContents(True)
        else:
            self.imgLabel.setPixmap(QPixmap("face-recognition.png"))
            self.dataPhoto.clear()
            self.NameLable.clear()
            # self.imgLabel.setScaledContents(True)
            # self.capture.release()







