from fastapi import FastAPI, File, UploadFile, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from gradio_client import Client, handle_file
from pathlib import Path
import shutil
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Initialize Gradio client
client = Client("jarif/Advanced-Bengali-Numeral-Recognition")

@app.get("/style.css")
async def get_css():
    return FileResponse("templates/style.css", media_type="text/css")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "result": None})

@app.post("/upload/")
async def upload_file(request: Request, file: UploadFile = File(...)):
    try:
        # Save the uploaded file temporarily
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process with Gradio client using handle_file
        result = client.predict(
            image=handle_file(temp_path),
            api_name="/predict"
        )
        
        # Clean up
        Path(temp_path).unlink()
        
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "result": result,
                "error": None
            }
        )
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "result": None,
                "error": f"Error processing image: {str(e)}"
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)