from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from beanie import init_beanie, Document
from bson import ObjectId
import io
from contextlib import asynccontextmanager

app = FastAPI(title="file Upload")

MONGO_URI = "mongodb://localhost:27017/"
client = AsyncIOMotorClient(MONGO_URI)
db = client["filedb"]
fs_bucket = AsyncIOMotorGridFSBucket(db)

class ExampleDoc(Document):
    name: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_beanie(database=db, document_models=[ExampleDoc])
    yield

app.router.lifespan_context = lifespan

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    if not file or not file.filename:
     raise HTTPException(status_code=400, detail="No file uploaded. Please upload a file.")
   # contents = await file.read()
    metadata = {"filename": file.filename, "content_type": file.content_type}
    file_id = await fs_bucket.upload_from_stream(
        file.filename,file.file, metadata=metadata,
    ) # io.BytesIO(contents)
    return {"file_id": str(file_id)}

@app.get("/download/{file_id}")
async def download_file(file_id: str):
    try:
        oid = ObjectId(file_id)
        grid_out = await fs_bucket.open_download_stream(oid)
        file_data = await grid_out.read()
        filename = grid_out.metadata.get("filename", "file")
        content_type = grid_out.metadata.get("content_type", "application/octet-stream")
        return StreamingResponse(
            io.BytesIO(file_data),
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception:
        raise HTTPException(status_code=404, detail="File not found")