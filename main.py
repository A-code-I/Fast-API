from fastapi import FastAPI, File, UploadFile,HTTPException
from fastapi.responses import JSONResponse,FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List
from lxml import etree
import httpx,os 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static HTML files at /static
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

xml_path=f"Telugu_Bible.xml"

def parse_bible_books():
    if not os.path.exists(xml_path):
        raise FileNotFoundError(f"File not found: {xml_path}")
    
    tree = etree.parse(xml_path)
    root = tree.getroot()

    books = [book.get("bname") for book in root.findall("BIBLEBOOK") if book.get("bname")]
    return books

@app.get("/get_books")
def get_books():
    try:
        books = parse_bible_books()
        return {"books": books}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def load_bible_xml():
    if not os.path.exists(xml_path):
        raise FileNotFoundError(f"File Not found {xml_path}")
    tree = etree.parse(xml_path)
    return tree.getroot()

@app.get("/books")
def get_books():
    try:
        root = load_bible_xml()
        books = [book.get("bname") for book in root.findall("BIBLEBOOK")]
        return {"books": books}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/books/{book_name}/chapters")
def get_chapters(book_name: str):
    try:
        root = load_bible_xml()
        for book in root.findall("BIBLEBOOK"):
            if book.get("bname") == book_name:
                chapters = [chapter.get("cnumber") for chapter in book.findall("CHAPTER")]
                return {"book": book_name, "chapters": chapters}
        raise HTTPException(status_code=404, detail=f"Book '{book_name}' not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/books/{book_name}/chapters/{chapter_number}/verses")
def get_verses(book_name: str, chapter_number: str):
    try:
        root = load_bible_xml()
        for book in root.findall("BIBLEBOOK"):
            if book.get("bname") == book_name:
                for chapter in book.findall("CHAPTER"):
                    if chapter.get("cnumber") == chapter_number:
                        verses = {
                            verse.get("vnumber"): verse.text.strip()
                            for verse in chapter.findall("VERS")
                        }
                        return {
                            "book": book_name,
                            "chapter": chapter_number,
                            "verses": verses
                        }
                raise HTTPException(status_code=404, detail=f"Chapter '{chapter_number}' not found.")
        raise HTTPException(status_code=404, detail=f"Book '{book_name}' not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
            
@app.get("/verse/random")
async def get_random_verse():
    url=f"https://bible-api.com/data/web/random"
    async with httpx.AsyncClient() as client:
        response=await client.get(url)

    if response.status_code!=200:
        raise HTTPException(status_code=404,detail="verse randomly not fetched")
    
    data=response.json()
    # formatted = f"{data['book']} {data['chapter']}:{data['verse']} - {data['text'].strip()}"
    return data


    return bible_verses["philippians_4_6"]

@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    # Optionally read the file contents
    contents = await file.read()
    file_size = len(contents)
    # You can save the file or process it here
    # For example, save to disk:
    with open(f"{file.filename}", "wb") as f:
        f.write(contents)
    return {"filename": file.filename, "content_type": file.content_type, "size": file_size}

@app.get("/media/{image_name}")
async def get_image(image_name: str):
    file_path = f"{image_name}"
    return FileResponse(path=file_path)

@app.get('/')  #path(/) operation(get) Decorator
async def root():
    return {'Message':'Hello API User..'}

@app.get('/{item_id}')  #path parameter 
def show_id(item_id:int):   #path parameters with types  ...validation happens from pydantic
    return {'Message':'Hello API User..',"id":item_id}
