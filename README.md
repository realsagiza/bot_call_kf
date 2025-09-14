# Chatbot (Dockerized)

โปรเจ็คนี้ประกอบด้วย
- Backend: FastAPI (Python) เชื่อมต่อ OpenAI GPT-5
- Frontend: React + Vite สำหรับทดสอบ UI แชทบอท
- Docker Compose สำหรับรันทั้งระบบแบบรวดเร็ว

## สเปค/รีไควเม้นต์ (Spec)
- มี UI ง่ายๆ สำหรับส่งข้อความและแสดงคำตอบของ AI
- มี API หลังบ้านสำหรับประมวลผลและเชื่อมต่อ OpenAI รุ่น `gpt-5`
- ทั้งหมดต้องรันบน Docker (ไม่ต้องเตรียมเครื่องล่วงหน้า)
- ไม่ใช้ mock ใดๆ ต้องเชื่อมต่อกับ OpenAI จริง (ต้องมีคีย์)
- ถ้าโค้ดยาวใกล้ 500 บรรทัดจะแยกเป็นไฟล์/โมดูลย่อยให้เหมาะสม

## โครงสร้างโปรเจ็ค
```
.
├─ backend/
│  ├─ app/
│  │  ├─ __init__.py
│  │  └─ main.py            # FastAPI + /api/chat
│  ├─ Dockerfile
│  └─ requirements.txt
├─ frontend/
│  ├─ src/
│  │  ├─ main.jsx
│  │  └─ widgets/Chat.jsx   # UI แชทอย่างง่าย
│  ├─ index.html
│  ├─ package.json
│  ├─ vite.config.js
│  └─ Dockerfile
├─ docker-compose.yml
├─ .gitignore
└─ README.md
```

## การตั้งค่า Environment
สร้างไฟล์ `.env` ที่รากโปรเจ็ค (ระดับเดียวกับ `docker-compose.yml`) ด้วยค่า:
```
OPENAI_API_KEY=ใส่คีย์ของคุณ
OPENAI_MODEL=gpt-5
```

> หมายเหตุ: ฝั่ง frontend จะอ่านตัวแปร `VITE_BACKEND_URL` จาก service env ใน compose แล้วชี้ไปที่ `http://localhost:8000` ตอนรันแบบ dev ผ่าน Docker

## วิธีรันด้วย Docker
1) สร้างไฟล์ `.env` ตามด้านบนให้เรียบร้อย
2) รันคำสั่ง:
```bash
docker compose up --build
```
3) เปิดเบราว์เซอร์:
- Backend: `http://localhost:8000/docs` (Swagger UI)
- Frontend: `http://localhost:5173`

## การใช้งาน API แบบตรง
- Endpoint: `POST /api/chat`
- รูปแบบตัวอย่าง payload:
```json
{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello"}
  ],
  "temperature": 0.7
}
```
- ผลลัพธ์:
```json
{"reply": "...ข้อความจาก AI..."}
```

## หมายเหตุเรื่องโมเดล
- โค้ดตั้งค่าเริ่มต้นเป็น `gpt-5` ผ่าน env `OPENAI_MODEL` คุณสามารถปรับได้ใน `.env` หรือส่ง `model` มากับ body ได้

## Development Tips
- โหมด dev ใช้ volume mount เพื่อแก้โค้ดได้ทันที (hot reload)
- ถ้าจะ build frontend สำหรับ production สามารถรัน `npm run build` ในคอนเทนเนอร์ และเสิร์ฟผ่าน static server เพิ่มเติมได้ (สามารถเพิ่ม service Nginx ภายหลังได้)

## License
MIT
