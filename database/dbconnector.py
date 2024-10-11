from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from mysql.connector import connect

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/database", response_class=HTMLResponse)
async def read_data(request: Request):
    # สร้างการเชื่อมต่อกับ MySQL
    connection = connect(
        host="localhost",
        user="root",
        password="",
        database="filterlab"
    )

    cursor = connection.cursor()
    
    # ตัวอย่างการรันคำสั่ง SQL
    cursor.execute("SELECT file_address FROM object")
    
    # ดึงข้อมูลทั้งหมดจากผลลัพธ์ของคำสั่ง
    results = cursor.fetchall()

    
    # วิธีใช้ results[i][0]
    for i in results:
        print(i[0])
    
    # ปิดการเชื่อมต่อ
    cursor.close()
    connection.close()

    # ส่งข้อมูลไปยัง HTML template ของคุณ
    return templates.TemplateResponse("workarea.html", {"request": request, "data": results}) # ใช้ใน html เรียกใช้ค่า data[i][0]