from all_class import *
import cv2
from PIL import Image, ImageDraw, ImageFont
import dlib
import numpy as np
from ultralytics import YOLO
import traceback
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, File, UploadFile
from websockets.exceptions import ConnectionClosed
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn    #  WEBSOCKET
import asyncio
import cv2
from ultralytics import YOLO
import torch
import json
from starlette.requests import Request
from mysql.connector import connect, Error
import shutil
import os


# print("CUDA Available:", torch.cuda.is_available())
# print("CUDA Device Count:", torch.cuda.device_count())

# Global Variables
WIDTH = 640
HEIGHT = 480
OBJECT = None
LEFT_EYE = None
RIGHT_EYE = None
LIP = None
TEXT = None
BG = None

# Model
detector = dlib.get_frontal_face_detector() # โมเดลตรวจจับใบหน้า (Face Detector)
predictor = dlib.shape_predictor('model/for face landmark.dat') # โมเดลตรวจจับ landmark บนใบหน้า
for_object = YOLO("model/for object segment.pt")
for_people = YOLO("model/for people segment.pt")

# ฟังก์ชันที่ทำงานแบบ Automate
def add_people_on_canvas(canvas, people):
    canvas.people = people
def update_canvas_on_camera(canvas):
    """ ฟังก์ชันสำหรับอัพเดท canvas ระหว่างที่กล้องทำงาน """
    canvas.canvas = canvas.update_canvas()

# ฟังก์ชันที่ทำงานเมื่อกดปุ่ม
def add_object_on_canvas(canvas, path):
    """ ฟังก์ชันสำหรับเพิ่ม object ลงใน canvas """
    object = Object(path, for_object)
    canvas.object_segment = canvas.resize_object(object.segment)

def add_background_on_canvas(canvas, path):
    """ ฟังก์ชันสำหรับเพิ่ม bg ลงใน canvas """
    background = canvas.resize_background(path)
    canvas.background = background

def add_text_on_canvas(canvas, text= 'ท้อเหมียนหมา'):
    # กำหนดค่าเริ่มต้น
    font_path = 'font/MalaiThin.ttf'
    image_size = (500, 150)
    text_color = "black"
    bg_color = (255, 255, 255, 0)

    # สร้างภาพขนาดตามที่กำหนดและกำหนดพื้นหลังเป็นโปร่งใส
    img = Image.new('RGBA', image_size, bg_color)
    d = ImageDraw.Draw(img)

    # เริ่มต้นขนาดฟอนต์ที่ใหญ่ที่สุดแล้วปรับลดจนกว่าข้อความจะพอดีกับภาพ
    font_size = 100  # ขนาดฟอนต์เริ่มต้น
    font = ImageFont.truetype(font_path, font_size)
    text_bbox = d.textbbox((0, 0), text, font=font)

    # ลดขนาดฟอนต์เมื่อข้อความล้นกรอบภาพ
    while text_bbox[2] - text_bbox[0] > image_size[0] or text_bbox[3] - text_bbox[1] > image_size[1]:
        font_size -= 5  # ลดขนาดฟอนต์
        font = ImageFont.truetype(font_path, font_size)
        text_bbox = d.textbbox((0, 0), text, font=font)

    # คำนวณตำแหน่งของข้อความให้อยู่กึ่งกลาง
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    position = ((image_size[0] - text_width) // 2, (image_size[1] - text_height) // 2)

    # วาดข้อความลงบนภาพ
    d.text(position, text, fill=text_color, font=font)

    canvas.text = canvas.resize_text(img)

def change_right_eye_xpos(canvas, number):
    """ ฟังก์ชันสำหรับปรับตำแหน่งซ้าย-ขวาของตาขวา """
    canvas.right_eye_position = (canvas.right_eye_position[0] + number, canvas.right_eye_position[1])

def change_right_eye_ypos(canvas, number):
    """ ฟังก์ชันสำหรับปรับตำแหน่งบน-ล่างของตาขวา """
    canvas.right_eye_position = (canvas.right_eye_position[0], canvas.right_eye_position[1] - number)

def change_right_eye_angle(canvas, number):
    """ ฟังก์ชันสำหรับปรับมุมของตาขวา """
    canvas.right_eye_angle += number

def change_left_eye_xpos(canvas, number):
    """ ฟังก์ชันสำหรับปรับตำแหน่งซ้าย-ขวาของตาซ้าย """
    canvas.left_eye_position = (canvas.left_eye_position[0] + number, canvas.left_eye_position[1])

def change_left_eye_ypos(canvas, number):
    """ ฟังก์ชันสำหรับปรับตำแหน่งบน-ล่างของตาซ้าย """
    canvas.left_eye_position = (canvas.left_eye_position[0], canvas.left_eye_position[1] - number)

def change_left_eye_angle(canvas, number):
    """ ฟังก์ชันสำหรับปรับมุมของตาซ้าย """
    canvas.left_eye_angle += number

def change_lips_xpos(canvas, number):
    """ ฟังก์ชันสำหรับปรับตำแหน่งซ้าย-ขวาของปาก """
    canvas.lips_position = (canvas.lips_position[0] + number, canvas.lips_position[1])

def change_lips_ypos(canvas, number):
    """ ฟังก์ชันสำหรับปรับตำแหน่งบน-ล่างของปาก """
    canvas.lips_position = (canvas.lips_position[0], canvas.lips_position[1] - number)

def change_lips_angle(canvas, number):
    """ ฟังก์ชันสำหรับปรับมุมของปาก """
    canvas.lips_angle += number

app = FastAPI()

templates = Jinja2Templates(directory="templates") # กำหนดตำแหน่งโฟล์เดอร์ทำงาน
app.mount("/static", StaticFiles(directory="templates/static"), name="static") # กำหนดตำแหน่งโฟล์เดอร์ static files

# การเชื่อมต่อกับ API แบบ default
@app.get('/')
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get('/filterlab')
def workarea(request: Request):
    return templates.TemplateResponse("workarea.html", {"request": request})

# การทำงานเมื่อมีการเชื่อมต่อ websocket
@app.websocket("/ws")
async def get_stream(websocket: WebSocket):
    global LEFT_EYE, RIGHT_EYE, LIP, OBJECT, WIDTH, HEIGHT, TEXT, BG
    await websocket.accept()

    camera = cv2.VideoCapture(0) #camera = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # ลดความกว้าง
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # ลดความสูง

    # ตรวจสอบว่ากล้องเปิดสำเร็จหรือไม่
    if not camera.isOpened():
            print("ไม่สามารถเปิดกล้องได้")
            exit()
    else:
            print("กล้องกำลังทำงาน")

    canvas = Canvas((640, 480))

    try:
        while True:
            try:
                success, frame = camera.read()
                print(type(frame))
                if not success:
                    break
                else:
                    temp_frame_path = 'temp_frame.jpg'
                    cv2.imwrite(temp_frame_path, frame)

                    # สร้าง people จาก People class โดยใช้เฟรมจากกล้อง
                    people = People(temp_frame_path, for_people, detector, predictor)
                    add_people_on_canvas(canvas, people)

                    # ทดสอบ
                    if TEXT != None:
                        add_text_on_canvas(canvas, TEXT)
                    if BG != None:
                        add_background_on_canvas(canvas, BG)
                    if OBJECT != None:
                        add_object_on_canvas(canvas, OBJECT)
                    update_canvas_on_camera(canvas)

                    image = np.array(canvas.canvas)
                    image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)

                    result_path = 'result.jpg'
                    cv2.imwrite(result_path, image)
                    ret, buffer = cv2.imencode('.jpg', image)
                    await websocket.send_bytes(buffer.tobytes())

                await asyncio.sleep(0.03)
            except Exception as e:
                print(f"เกิดข้อผิดพลาด: {e}")
                print(traceback.format_exc())
                await websocket.send_text("error")
    except (WebSocketDisconnect, ConnectionClosed):
        print("Client disconnected")

@app.post("/reset-variables")
async def reset_variables():
    global OBJECT, TEXT, BG
    # Reset the variables
    OBJECT = None
    BG = None
    TEXT = None
    return {"message": "Variables reset successfully"}

@app.websocket("/mask_data")
async def mask_data(websocket: WebSocket):
    """
    รับค่าตัวแปร
    """
    await websocket.accept()
    data = await websocket.receive_text()
    print(f"Received config data: {data}")

    data_dict = json.loads(data)
    global LEFT_EYE, RIGHT_EYE, LIP, OBJECT, WIDTH, HEIGHT
    LEFT_EYE = data_dict.get("LEFT_EYE", None)
    RIGHT_EYE = data_dict.get("RIGHT_EYE", None)
    LIP = data_dict.get("LIP", None)
    OBJECT = data_dict.get("OBJECT", None)
    WIDTH = data_dict.get("width", None)
    HEIGHT = data_dict.get("height", None)

@app.websocket("/text_data")
async def text_data(websocket: WebSocket):
    """
    รับค่าตัวแปร
    """
    await websocket.accept()
    data = await websocket.receive_text()
    print(f"Received config data: {data}")

    data_dict = json.loads(data)
    global TEXT, WIDTH, HEIGHT
    TEXT = data_dict.get("TEXT", None)
    WIDTH = data_dict.get("width", None)
    HEIGHT = data_dict.get("height", None)

@app.websocket("/bg_data")
async def bg_data(websocket: WebSocket):
    """
    รับค่าตัวแปร
    """
    await websocket.accept()
    data = await websocket.receive_text()
    print(f"Received config data: {data}")

    data_dict = json.loads(data)
    global BG, WIDTH, HEIGHT
    BG = data_dict.get("BG", None)
    WIDTH = data_dict.get("width", None)
    HEIGHT = data_dict.get("height", None)


@app.websocket("/database")
async def database(websocket: WebSocket):
    await websocket.accept()  # Accept the WebSocket connection

    try:
        # Create a connection to MySQL
        connection = connect(
            host="localhost",
            user="root",
            password="",
            database="filterlab"
        )

        cursor = connection.cursor()

        # Example SQL command to select specific columns
        cursor.execute("SELECT file_id, filter_path FROM filters")

        # Fetch all results from the query
        results = cursor.fetchall()

        # Log the results for debugging
        for i in results:
            print(i)

        # Prepare data to be sent as JSON
        data_to_send = [{"file_id": row[0], "filter_path": row[1]} for row in results]

        # Send the results as a JSON string
        await websocket.send_text(json.dumps(data_to_send))

    except Error as e:
        print(f"Error: {e}")
        await websocket.send_text(json.dumps({"error": str(e)}))  # Send error message back to client

    finally:
        # Ensure that the cursor and connection are closed
        if cursor:
            cursor.close()
        if connection:
            connection.close()

        await websocket.close()  # Close the WebSocket connection

@app.websocket("/filter_data")
async def filter_data(websocket: WebSocket):
    """
    รับค่าตัวแปร
    """
    await websocket.accept()
    data = await websocket.receive_text()
    print(f"Received config data: {data}")

    data_dict = json.loads(data)
    global LEFT_EYE, RIGHT_EYE, LIP, OBJECT, WIDTH, HEIGHT, TEXT, BG
    LEFT_EYE = data_dict.get("LEFT_EYE", None)
    RIGHT_EYE = data_dict.get("RIGHT_EYE", None)
    LIP = data_dict.get("LIP", None)
    OBJECT = data_dict.get("OBJECT", None)
    TEXT = data_dict.get("TEXT", None)
    BG = data_dict.get("BG", None)
    WIDTH = data_dict.get("width", None)
    HEIGHT = data_dict.get("height", None)

@app.websocket("/database_filter")
async def database_filter(websocket: WebSocket):
    await websocket.accept()
    data = await websocket.receive_text()
    data_dict = json.loads(data)  # Parse the received JSON data

    file_id = data_dict.get("file_id")
    try:
        # Create a connection to MySQL
        connection = connect(
            host="localhost",
            user="root",
            password="",
            database="filterlab"
        )

        cursor = connection.cursor()
        query = "SELECT * FROM filters WHERE file_id = %s"
        cursor.execute(query, (file_id,))
        result = cursor.fetchone()

        if result:
            # Map the result to column names or keys for easier handling
            row_data = {
                "file_id": result[0],
                "name": result[1],
                "filter_path": result[2],
                "text": result[3],
                "object_path": result[4],  #
                "bg_path": result[5]
            }

            # Send the result back as JSON
            await websocket.send_text(json.dumps(row_data))
        else:
            await websocket.send_text(json.dumps({"error": "No row found for the given file_id"}))


        cursor.close()
        connection.close()

    except WebSocketDisconnect:
        print("WebSocket connection closed")

UPLOAD_FOLDER = "./templates/static/img/"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
@app.post("/")
async def save_image(imagefile: UploadFile = File(...)):
    image_path = os.path.join(UPLOAD_FOLDER, imagefile.filename)

    # Save the uploaded image to the specified path
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(imagefile.file, buffer)

    return {"filename": imagefile.filename, "status": "Upload successful", "path": image_path}


if __name__ == "__main__":
    uvicorn.run(app, host='localhost', port=8000)
