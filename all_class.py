""" class """
# from PIL import Image, ImageDraw, ImageFont
from PIL import Image
import cv2
import numpy as np

class People():
    """ people """
    def __init__(self, path, model, detector, predictor):
        self.path = path
        self.size = Image.open(self.path).size
        self.people = Image.open(self.path).convert("RGBA")  # พร้อมเข้า canvas
        self.people_numpy = cv2.imread(self.path)
        self.all_points = self.__get_all_points(model, detector, predictor)
        self.people_points = self.all_points[0] if self.all_points is not None else None
        self.nose_tip_point = self.all_points[1] if self.all_points is not None else None
        self.left_eye_points = self.all_points[2] if self.all_points is not None else None
        self.right_eye_points = self.all_points[3] if self.all_points is not None else None
        self.lips_points = self.all_points[4] if self.all_points is not None else None
        self.left_eye_extend_points = self.all_points[5] if self.all_points is not None else None
        self.right_eye_extend_points = self.all_points[6] if self.all_points is not None else None
        self.lips_extend_points = self.all_points[7] if self.all_points is not None else None
        self.face_width = self.all_points[8] if self.all_points is not None else None
        self.face_height = self.all_points[9] if self.all_points is not None else None
        self.between_eyebrow_point = self.all_points[10] if self.all_points is not None else None
        self.people_segment = self.__get_people_segment()  # รูปคนที่พร้อมเข้า Canvas เพื่อ overlay
        self.left_eye_segment = self.__get_lips_eyes_segment(self.left_eye_points,
                                                             self.left_eye_extend_points)  # พร้อมเข้า Canvas เพื่อ overlay
        self.right_eye_segment = self.__get_lips_eyes_segment(self.right_eye_points,
                                                              self.right_eye_extend_points)  # พร้อมเข้า Canvas เพื่อ overlay
        self.lips_segment = self.__get_lips_eyes_segment(self.lips_points,
                                                         self.lips_extend_points)  # พร้อมเข้า Canvas เพื่อ overlay
    def __get_all_points(self, model, detector, predictor):
        """ ฟังก์ชันสำหรับหาจุดของ object จากโมเดล """
        model_segment = model(self.path)
        if len(model_segment) == 0:  # ถ้าไม่พบ object ในภาพ
            return None
        else:
            people_points = model_segment[0][0].masks.xy[0]  # เอาวัตถุที่ตรวจจับได้ % เยอะที่สุด
            people_points = [tuple(i) for i in people_points]

        gray = cv2.cvtColor(self.people_numpy, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)  # ตรวจจับใบหน้าในภาพ

        if len(faces) == 0:  # ถ้าไม่พบใบหน้าในภาพ
            return None
        elif len(faces) > 0:  # ถ้าพบหลายใบหน้าในภาพ

            for face in faces:  # วนลูปในใบหน้าที่ถูกตรวจจับได้

                face_width = face.right() - face.left()
                face_height = face.bottom() - face.top()

                landmarks = predictor(gray, face)  # หาจุด landmark บนใบหน้า

                nose_tip_point = (landmarks.part(30).x, landmarks.part(30).y)

                between_eyebrow_point = (landmarks.part(27).x, (landmarks.part(27).y) - 30)

                left_eye_points = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)]  # จุดของตา
                right_eye_points = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)]  # จุดของตา
                lips_points = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(48, 60)]  # จุดของปาก

                left_eye_extend_points = left_eye_points.copy()  # จุดของตาเพิ่มเติม
                right_eye_extend_points = right_eye_points.copy()  # จุดของตาเพิ่มเติม
                lips_extend_points = lips_points.copy()  # จุดของปากเพิ่มเติม

                eye_lip_mappings = {range(36, 42): left_eye_extend_points,\
                                    range(42, 48): right_eye_extend_points,\
                                    range(48, 60): lips_extend_points}
                adjustments = {36: (-5, 0), 37: (-5, -5), 38: (5, -5), 39: (5, 0), 40: (5, 5), 41: (-5, 5),\
                               42: (-5, 0), 43: (-5, -5), 44: (5, -5), 45: (5, 0), 46: (5, 5), 47: (-5, 5),\
                                48: (-5, 0), 49: (-5, -5), 50: (-5, -5), 51: (0, -5), 52: (5, -5), 53: (5, -5),\
                                    54: (5, 0), 55: (5, 5), 56: (5, 5), 57: (0, 5), 58: (-5, 5), 59: (-5, 5)}

                for n in range(36, 60): # เข้า loop เพื่อทำตาปากเพิ่มเติม
                    x = landmarks.part(n).x
                    y = landmarks.part(n).y
                    x_adj, y_adj = adjustments[n]

                    # Determine which list to append to based on n's range
                    for key_range, extend_points in eye_lip_mappings.items():
                        if n in key_range:
                            extend_points.append((x + x_adj, y + y_adj))

                all_points = [people_points, nose_tip_point, left_eye_points, right_eye_points, lips_points,
                              left_eye_extend_points, \
                              right_eye_extend_points, lips_extend_points, face_width, face_height, between_eyebrow_point]
                return all_points

    def __draw_polygon(self, mask, points, color=255):
        """ ฟังก์ชันสำหรับวาดโพลิกอนสีขาวบน mask """
        points = np.array(points, dtype=np.int32)
        cv2.fillPoly(mask, [points], color)

    def __get_people_segment(self):
        """ ฟังก์ชันสำหรับทำการ segment คน """
        if self.all_points is None:
            return None
        mask = np.zeros((self.people_numpy.shape[0], self.people_numpy.shape[1]),
                        dtype=np.uint8)  # สร้าง mask เปล่าที่มีขนาดเท่ากับภาพต้นฉบับ (ภาพสีดำ)
        self.__draw_polygon(mask, self.people_points, 255)  # วาด object ลงบน mask
        kernel = np.ones((2, 2), np.uint8)  # กำหนดขนาดของ kernel
        mask = cv2.erode(mask, kernel, iterations=5)  # ใช้ erosion เพื่อลดขนาดของ mask และทำให้ขอบดูนุ่มลง
        mask = cv2.dilate(mask, kernel, iterations=1)  # ใช้ dilation ถ้าต้องการทำให้ขอบใหญ่ขึ้นอีกเล็กน้อย (optional)
        masked_image = cv2.bitwise_and(self.people_numpy, self.people_numpy,
                                       mask=mask)  # ใช้ mask กับภาพต้นฉบับ (รักษาความโปร่งใส)
        alpha_channel = np.where(mask > 0, 255, 0).astype(
            np.uint8)  # สร้างช่อง alpha เพื่อทำให้ส่วนอื่นๆ โปร่งใส # ถ้า mask > 0 ให้ alpha=255, ถ้าไม่ใช่ให้ alpha=0
        segment = np.dstack((masked_image, alpha_channel))  # รวม RGB กับ alpha เป็น RGBA
        segment = cv2.cvtColor(segment, cv2.COLOR_BGRA2RGBA)  # แปลงภาพสี BGRA เป็น RGBA เพื่อให้สีไม่เพี้ยนจากเดิม
        segment = Image.fromarray(segment, 'RGBA')  # แปลง format เป็น PIT ให้สามารถ overlay ได้
        return segment

    def __get_lips_eyes_segment(self, points, points_extend):
        """ ฟังก์ชันสำหรับทำการ segment ตาและปาก """
        if self.all_points is None:
            return None
        mask = np.zeros((self.people_numpy.shape[0], self.people_numpy.shape[1]),
                        dtype=np.uint8)  # สร้าง mask เปล่าที่มีขนาดเท่ากับภาพต้นฉบับ (ภาพสีดำ)
        self.__draw_polygon(mask, points, 255)  # วาดตา mask โดยทำส่วนตา หรือ ปากให้เป็นสีขาว (ส่วนที่ == 255)
        masked_image = cv2.bitwise_and(self.people_numpy, self.people_numpy,
                                       mask=mask)  # ใช้ mask กับภาพต้นฉบับ (รักษาความโปร่งใส)
        alpha_channel = np.where(mask == 255, 255, 0).astype(np.uint8)  # ถ้าสีขาวให้ alpha=255, ถ้าไม่ใช่ให้ alpha=0
        result = np.dstack((masked_image, alpha_channel))  # รวม RGB กับ alpha เป็น RGBA
        result = cv2.cvtColor(result, cv2.COLOR_BGRA2RGBA)
        result = Image.fromarray(result)  # แปลง format lips_eyes ให้สามารถ overlay ได้

        mask_extend = np.zeros((self.people_numpy.shape[0], self.people_numpy.shape[1]),
                               dtype=np.uint8)  # Use shape instead of size for numpy arrays
        self.__draw_polygon(mask_extend, points_extend, 255)
        # เบลอ mask_extend ด้วย Gaussian Blur หรือ Median Blur หรือ Bilateral Filter
        blurred_mask_extend = cv2.GaussianBlur(mask_extend, (21, 21), 0)  # ขนาด kernel 31x31
        # สร้าง alpha channel จาก mask ที่เบลอ (คำนวณจากค่า 0-255)
        alpha_channel_extend = blurred_mask_extend.astype(np.uint8)  # ใช้ mask เบลอเป็น alpha channel
        # สร้างภาพ RGBA จากภาพต้นฉบับ (people_image)
        rgba_image = cv2.cvtColor(self.people_numpy, cv2.COLOR_BGR2BGRA)
        # แทนที่ alpha channel ในภาพ RGBA ด้วย alpha channel ที่เบลอ
        rgba_image[:, :, 3] = alpha_channel_extend
        # แปลงภาพกลับเป็น Image format ของ PIL สำหรับการ overlay
        result_extend = cv2.cvtColor(rgba_image, cv2.COLOR_BGRA2RGBA)
        result_extend = Image.fromarray(result_extend)

        combined_result = Image.alpha_composite(result, result_extend)
        return combined_result

class Object():
    """ object """
    def __init__(self, path, model):
        self.path = path
        self.object_numpy = cv2.imread(self.path)
        self.file_extension = self.__check_file_extension()
        self.points = self.__get_points(model)
        self.segment = self.__get_segment()  # รูปที่พร้อมเข้า Canvas เพื่อ overlay

    def __check_file_extension(self):
        """ ฟังก์ชันสำหรับเช็คนามสกุลไฟล์ """
        if self.path.endswith('.jpg') or self.path.endswith('.jpeg'):
            return 'jpg'
        elif self.path.endswith('.png'):
            return 'png'
        else:
            return None

    def __get_points(self, model):
        """ ฟังก์ชันสำหรับหาจุดของ obect จากโมเดล """
        if self.file_extension == 'jpg':  # object ยังไม่แยก ต้องหาจุดเพื่อไปทำ segment
            model_segment = model(self.path)
            points = model_segment[0][0].masks.xy[0]  # เอาวัตถุที่ตรวจจับ % เยอะที่สุด
            points = [tuple(i) for i in points]
            return points
        elif self.file_extension == 'png':  # object แยกมาอยู่แล้ว ไม่ต้องทำ segment
            return []

    def __draw_polygon(self, mask, points, color=255):
        """ ฟังก์ชันสำหรับวาดโพลิกอนสีขาวบน mask """
        points = np.array(points, dtype=np.int32)
        cv2.fillPoly(mask, [points], color)

    def __get_segment(self):
        """ ฟังก์ชันสำหรับทำการ segment object """
        if self.file_extension == 'jpg':
            mask = np.zeros((self.object_numpy.shape[0], self.object_numpy.shape[1]),
                            dtype=np.uint8)  # สร้าง mask เปล่าที่มีขนาดเท่ากับภาพต้นฉบับ (ภาพสีดำ)
            self.__draw_polygon(mask, self.points, 255)  # วาด object ลงบน mask
            kernel = np.ones((2, 2), np.uint8)  # กำหนดขนาดของ kernel
            mask = cv2.erode(mask, kernel, iterations=5)  # ใช้ erosion เพื่อลดขนาดของ mask และทำให้ขอบดูนุ่มลง
            mask = cv2.dilate(mask, kernel,
                              iterations=1)  # ใช้ dilation ถ้าต้องการทำให้ขอบใหญ่ขึ้นอีกเล็กน้อย (optional)
            masked_image = cv2.bitwise_and(self.object_numpy, self.object_numpy,
                                           mask=mask)  # ใช้ mask กับภาพต้นฉบับ (รักษาความโปร่งใส)
            alpha_channel = np.where(mask > 0, 255, 0).astype(
                np.uint8)  # สร้างช่อง alpha เพื่อทำให้ส่วนอื่นๆ โปร่งใส # ถ้า mask > 0 ให้ alpha=255, ถ้าไม่ใช่ให้ alpha=0
            segment = np.dstack((masked_image, alpha_channel))  # รวม RGB กับ alpha เป็น RGBA
            segment = cv2.cvtColor(segment, cv2.COLOR_BGRA2RGBA)  # แปลงภาพสี BGRA เป็น RGBA เพื่อให้สีไม่เพี้ยนจากเดิม
            segment = Image.fromarray(segment, 'RGBA')  # แปลง format เป็น PIT ให้สามารถ overlay ได้
            return segment
        else:
            segment = Image.open(self.path).convert("RGBA")
            return segment

class Canvas():
    """ canvas """
    def __init__(self, size, people=None, object_segment=None, background=None, text=None):
        self.size = size
        self.people = people
        self.object_segment = self.resize_object(object_segment)
        self.text = self.resize_text(text)
        self.background = self.resize_background(background)
        self.images_with_positions = []
        self.canvas = Image.new("RGBA", self.size, (0, 0, 0, 0))  # รูปที่ overlay เสร็จแล้ว มาจากฟังก์ชันที่สร้าง default ต้องมีคนอยู่ในนั้น ถ้ามี object เพิ่มต้องมีฟังก์ชันอัพเดท
        self.object_position = self.__get_object_position()
        self.left_eye_position: tuple[int, int] = (0, 0)
        self.right_eye_position: tuple[int, int] = (0, 0)
        self.lips_position: tuple[int, int] = (0, 0)
        self.left_eye_angle = 0
        self.right_eye_angle = 0
        self.lips_angle = 0

    def update_canvas(self):
        """ ฟังก์ชันสำหรับอัพเดท canvas """
        self.images_with_positions = [(self.people.people, (0, 0), 0)]
        if self.background is None:
            if self.object_segment is not None: # ไม่มี bg มี object
                self.images_with_positions = [(self.people.people, (0, 0), 0), (self.resize_object(self.object_segment), self.object_position, 0)\
                                              ,(self.people.left_eye_segment, self.left_eye_position, self.left_eye_angle)\
                                                ,(self.people.right_eye_segment, self.right_eye_position, self.right_eye_angle)\
                                                    ,(self.people.lips_segment, self.lips_position, self.lips_angle)]
                if self.text is not None: # ไม่มี bg มี object มี text
                    self.images_with_positions.append((self.resize_text(self.text), self.text_position, 0))
            elif self.object_segment is None and self.text is not None: # ไม่มี bg ไม่มี object มีแค่ text
                self.images_with_positions = [(self.people.people, (0, 0), 0), ((self.resize_text(self.text)), self.text_position, 0)]
        if self.background is not None:
            if self.object_segment is None and self.text is None: # มี bg ไม่มี object ไม่มี text
                self.images_with_positions = [(self.background, (0, 0), 0), (self.people.people_segment, (0, 0), 0)]
            elif self.object_segment is not None: # มี bg มี object ไม่มี text
                self.images_with_positions = [(self.background, (0, 0), 0), (self.resize_object(self.object_segment), self.object_position, 0)\
                                              ,(self.people.left_eye_segment, self.left_eye_position, self.left_eye_angle)\
                                                ,(self.people.right_eye_segment, self.right_eye_position, self.right_eye_angle)\
                                                    ,(self.people.lips_segment, self.lips_position, self.lips_angle)]

                if self.text is not None: # มี bg มี object มี text
                    self.images_with_positions.append(((self.resize_text(self.text)), self.text_position, 0))

            elif self.object_segment is None and self.text is not None: # มี bg ไม่มี object มี text
                self.images_with_positions = [(self.background, (0, 0), 0), (self.people.people_segment, (0, 0), 0), ((self.resize_text(self.text)), self.text_position, 0)]

        canvas = Image.new("RGBA", self.size, (0, 0, 0, 0))
        for img, position, angle in self.images_with_positions:  # ดึงมุม (angle) สำหรับหมุนภาพ
            rotated_img = img.rotate(angle, expand=True)  # หมุนภาพตามมุมที่กำหนด, expand=True จะขยายภาพหลังหมุน
            canvas.paste(rotated_img, position, rotated_img)  # นำภาพที่หมุนแล้ววางบน canvas มีวิธีทำให้สั้นลงมั้ย
        return canvas
    @property
    def people(self):
        return self._people

    @people.setter
    def people(self, new_people):
        self._people = new_people
        self.object_position = self.__get_object_position()
        self.text_position = self.__get_text_position()

    def __get_object_position(self):
        """ ฟังก์ชันสำหรับหาตำแหน่งของ object """
        if self.people is None:
            return None
        x = self.people.nose_tip_point[0] - int(self.people.face_width * 1.4) // 2
        y = self.people.nose_tip_point[1] - int(self.people.face_height * 1.4) // 2
        return (x, y)

    def __get_text_position(self):
        """ ฟังก์ชันสำหรับหาตำแหน่งของ object """
        if self.people is None:
            return None
        x = self.people.between_eyebrow_point[0] - int(self.people.face_width * 1.4) // 2
        y = self.people.between_eyebrow_point[1] - int(self.people.face_height * 1.4) // 2
        return (x, y)

    def resize_text(self, text):
        """ ฟังก์ชันสำหรับปรับขนาด object ให้เข้ากับ รูปคน """
        if text is None:
            return None
        width, height = text.size
        new_width = int(self.people.face_width * 1.6)  # ขนาดใหม่ที่ใหญ่ขึ้น 40%
        new_height = int(height / width * new_width)
        text = text.resize((new_width, new_height))
        return text

    def resize_object(self, object_segment):
        """ ฟังก์ชันสำหรับปรับขนาด object ให้เข้ากับ รูปคน """
        if object_segment is None:
            return None
        new_width = int(self.people.face_width * 1.4)  # ขนาดใหม่ที่ใหญ่ขึ้น 40%
        new_height = int(self.people.face_height * 1.4)
        object = object_segment.resize((new_width, new_height))
        return object

    def resize_background(self, background):

        """ ฟังก์ชันสำหรับปรับขนาด bg ให้ครอบคลุมกับ canvas ซึ่งเป็นขนาดของจอโทรศัพท์ Full HD โดยรักษาสัดส่วน (aspect ratio)"""
        if background is None:
            return None
        background = Image.open(background).convert("RGBA")

        # คำนวณสัดส่วนการ resize ให้ครอบคลุม canvas
        background_ratio = max(self.size[0] / background.width, self.size[1] / background.height)
        new_size = (int(background.width * background_ratio), int(background.height * background_ratio))
        background = background.resize(new_size, Image.Resampling.LANCZOS)

        # ตัดบางส่วนของพื้นหลังหากใหญ่เกินไป (crop)
        left = (background.width - self.size[0]) // 2
        top = (background.height - self.size[1]) // 2
        right = left + self.size[0]
        bottom = top + self.size[1]
        background = background.crop((left, top, right, bottom))
        return background