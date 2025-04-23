from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QTimer
import cv2
import csv
import os

Form, Window = uic.loadUiType("res/mainWin.ui")

class MainWindow:
    def __init__(self):
        self.app = QApplication([])
        self.window = Window()
        self.form = Form()
        self.form.setupUi(self.window)
        self.capture = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        # btn_save 버튼 클릭 이벤트 연결
        self.form.btn_save.clicked.connect(self.save_data)
        self.form.btn_cam.clicked.connect(self.take_picture)
        self.form.btn_exit.clicked.connect(self.exit)

    def exit(self):
      self.capture.release()
      self.app.quit()

    def update_frame(self):
        ret, frame = self.capture.read()
        if ret:
            # OpenCV 이미지를 PyQt 이미지로 변환
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            self.form.lb_video.setPixmap(QPixmap.fromImage(qt_image))

    def take_picture(self):
        ret, frame = self.capture.read()
        if ret:
            # photos 폴더가 없으면 생성
            if not os.path.exists("photos"):
                os.makedirs("photos")
            
            # 파일명 처리 (한글 지원)
            raw_name = self.form.ed_name.text().strip() or "untitled"
            safe_name = "".join(c if c.isalnum() else "_" for c in raw_name)  # 특수문자 처리
            filename = os.path.join("photos", f"{safe_name}.jpg")
            
            # 이미지 저장
            try:
                # 파일명을 UTF-8로 인코딩하여 OpenCV가 처리할 수 있도록 함
                filename_encoded = os.path.abspath(filename).encode("utf-8")
                cv2.imencode('.jpg', frame)[1].tofile(filename_encoded)
                QMessageBox.information(None, "사진 저장", f"사진이 {filename}로 저장되었습니다!")
            except Exception as e:
                QMessageBox.critical(None, "오류", f"사진을 저장할 수 없습니다: {e}")
        else:
            QMessageBox.critical(None, "오류", "사진을 저장할 수 없습니다.")

    def save_data(self):
        # QLineEdit, QLabel, QTextEdit에서 텍스트 가져오기
        name = self.form.ed_name.text().strip()  # 이름
        phone = self.form.ed_phone.text().strip()  # 전화번호
        memo = self.form.ed_memo.toPlainText().strip()  # 메모

        # 데이터가 비어 있는지 확인
        if not name or not phone or not memo:
            QMessageBox.warning(None, "입력 오류", "모든 필드를 입력해주세요!")
            return

        # 텍스트 파일로 저장
        try:
            with open("studentList.txt", "a", encoding="utf-8") as txtfile:
                txtfile.write(f"{name}\t{phone}\t{memo}\n")
            QMessageBox.information(None, "저장 완료", "데이터가 성공적으로 저장되었습니다!")
        except Exception as e:
            QMessageBox.critical(None, "저장 실패", f"오류가 발생했습니다: {e}")

    def run(self):
        self.window.show()
        self.app.exec()

if __name__ == "__main__":
    main_window = MainWindow()
    main_window.run()