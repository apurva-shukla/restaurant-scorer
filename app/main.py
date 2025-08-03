from datetime import date
from typing import List, Optional
from fastapi import FastAPI, Form, Request, Depends, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel, Session, create_engine, select
import os
import uuid
from PIL import Image
import pillow_heif

from .models import ScoreEntry

# Register HEIF opener
pillow_heif.register_heif_opener()

# Create data directories if they don't exist
os.makedirs("data/uploads", exist_ok=True)

# Database setup
DATABASE_URL = "sqlite:///data/food.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# FastAPI app
app = FastAPI(title="Restaurant Scorer", description="A simple restaurant scoring webapp")

# Serve static files from the 'data' directory
app.mount("/data", StaticFiles(directory="data"), name="data")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Helper function to process and save images
async def process_and_save_image(file: UploadFile) -> Optional[str]:
    if not file or file.filename == "":
        return None

    # Generate unique filenames
    file_extension = os.path.splitext(file.filename)[1].lower()
    temp_filename = f"temp_{uuid.uuid4()}{file_extension}"
    temp_file_path = f"data/uploads/{temp_filename}"
    
    final_filename = f"{uuid.uuid4()}.jpg"  # Always save as JPEG
    final_file_path = f"data/uploads/{final_filename}"

    try:
        # Read and save the uploaded file temporarily
        file_content = await file.read()
        with open(temp_file_path, "wb") as buffer:
            buffer.write(file_content)
        
        # Check if it's a HEIF file and handle explicitly
        is_heif = file_extension in ['.heic', '.heif'] or file.filename.lower().endswith(('.heic', '.heif'))
        
        if is_heif:
            # Try multiple approaches for HEIF files
            img = None
            
            # Method 1: Direct pillow-heif approach
            try:
                import pillow_heif
                heif_file = pillow_heif.read_heif(temp_file_path)
                img = heif_file.to_pillow()
                print("Successfully processed HEIF using pillow-heif.read_heif()")
            except Exception as e1:
                print(f"Method 1 failed: {e1}")
                
                # Method 2: Try opening with registered opener
                try:
                    img = Image.open(temp_file_path)
                    print("Successfully processed HEIF using Pillow with registered opener")
                except Exception as e2:
                    print(f"Method 2 failed: {e2}")
                    
                    # Method 3: Try alternative pillow-heif approach
                    try:
                        import pillow_heif
                        heif_file = pillow_heif.open_heif(temp_file_path, convert_hdr_to_8bit=True)
                        img = heif_file.to_pillow()
                        print("Successfully processed HEIF using pillow-heif.open_heif() with HDR conversion")
                    except Exception as e3:
                        print(f"Method 3 failed: {e3}")
                        raise Exception(f"All HEIF processing methods failed: {e1}, {e2}, {e3}")
            
            if img is None:
                raise Exception("Could not process HEIF file with any method")
        else:
            # Use regular Pillow for other formats
            img = Image.open(temp_file_path)
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Resize and compress
        img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
        
        # Save as JPEG with compression
        img.save(final_file_path, "JPEG", quality=75, optimize=True)

        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

        return f"/data/uploads/{final_filename}"

    except Exception as e:
        print(f"Error processing image: {e}")
        print(f"File extension: {file_extension}, Is HEIF: {is_heif if 'is_heif' in locals() else 'Unknown'}")
        # Clean up any files that might have been created
        for path in [temp_file_path, final_file_path]:
            if os.path.exists(path):
                os.remove(path)
        return None


@app.post("/upload-image-preview", response_class=JSONResponse)
async def upload_image_preview(image: UploadFile):
    """Process an image upload and return a path for preview."""
    if not image:
        return JSONResponse(status_code=400, content={"error": "No file uploaded."})
    
    image_path = await process_and_save_image(image)

    if image_path:
        return {"image_path": image_path}
    else:
        return JSONResponse(status_code=500, content={"error": "Failed to process image."})


# Create database tables on startup
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the HTML form"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/submit")
async def submit_score(
    request: Request,
    restaurant_name: str = Form(...),
    gmaps_link: str = Form(...),
    date_visited: date = Form(...),
    mood: float = Form(...),
    taste: int = Form(...),
    experience: int = Form(...),
    value: int = Form(...),
    notes: str = Form(""),
    image_path_1: Optional[str] = Form(None),
    image_path_2: Optional[str] = Form(None),
    session: Session = Depends(get_session)
):
    """Accept form data with pre-processed image paths, compute final score, and insert into database"""
    
    # Calculate final score
    final_score = (taste + experience + value) / mood
    
    # Create new entry
    entry = ScoreEntry(
        restaurant_name=restaurant_name,
        gmaps_link=gmaps_link,
        date_visited=date_visited,
        mood=mood,
        taste=taste,
        experience=experience,
        value=value,
        notes=notes if notes else None,
        final_score=final_score,
        image_path_1=image_path_1,
        image_path_2=image_path_2
    )
    
    # Save to database
    session.add(entry)
    session.commit()
    session.refresh(entry)
    
    # Return success message for HTMX
    return HTMLResponse(
        content=f"""
        <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
            <strong>Success!</strong> Restaurant "{restaurant_name}" saved with a score of {final_score:.2f}
        </div>
        <script>clearForm();</script>
        """,
        status_code=200
    )

@app.get("/entries", response_model=List[ScoreEntry])
def list_entries(limit: int = 100, session: Session = Depends(get_session)):
    """List recent entries as JSON for API consumption"""
    entries = session.exec(
        select(ScoreEntry)
        .order_by(ScoreEntry.date_visited.desc())
        .limit(limit)
    ).all()
    return entries

@app.get("/history")
async def get_history(
    request: Request,
    sort_by: str = "date",  # "date" or "score"
    limit: int = 50,
    session: Session = Depends(get_session)
):
    """Return HTML formatted history of restaurant entries"""
    # Build the query with appropriate sorting
    query = select(ScoreEntry)
    
    if sort_by == "score":
        query = query.order_by(ScoreEntry.final_score.desc())
    else:  # default to date
        query = query.order_by(ScoreEntry.date_visited.desc())
    
    query = query.limit(limit)
    entries = session.exec(query).all()
    
    # Generate HTML response
    if not entries:
        html_content = """
        <div class="bg-gray-50 border border-gray-200 rounded-lg p-6 text-center">
            <p class="text-gray-600">No restaurant entries found yet.</p>
        </div>
        """
    else:
        entries_html = ""
        for entry in entries:
            # Format images if they exist
            images_html = ""
            if entry.image_path_1 or entry.image_path_2:
                images_html = '<div class="flex gap-2 mt-2">'
                if entry.image_path_1:
                    images_html += f'<img src="{entry.image_path_1}" class="w-16 h-16 object-cover rounded-lg" alt="Restaurant photo 1">'
                if entry.image_path_2:
                    images_html += f'<img src="{entry.image_path_2}" class="w-16 h-16 object-cover rounded-lg" alt="Restaurant photo 2">'
                images_html += '</div>'
            
            notes_html = ""
            if entry.notes:
                notes_html = f'<p class="text-sm text-gray-600 mt-2 italic">"{entry.notes}"</p>'
            
            entries_html += f"""
            <div class="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
                <div class="flex justify-between items-start mb-2">
                    <div>
                        <h3 class="font-semibold text-lg text-gray-800">
                            <a href="{entry.gmaps_link}" target="_blank" class="hover:text-blue-600 hover:underline">
                                {entry.restaurant_name}
                            </a>
                        </h3>
                        <p class="text-sm text-gray-500">Visited: {entry.date_visited.strftime('%B %d, %Y')}</p>
                    </div>
                    <div class="text-right">
                        <div class="text-2xl font-bold text-blue-600">{entry.final_score:.2f}</div>
                        <div class="text-xs text-gray-500">Final Score</div>
                    </div>
                </div>
                <div class="grid grid-cols-4 gap-4 text-sm">
                    <div class="text-center">
                        <div class="font-medium text-gray-700">{entry.taste}</div>
                        <div class="text-xs text-gray-500">Taste</div>
                    </div>
                    <div class="text-center">
                        <div class="font-medium text-gray-700">{entry.experience}</div>
                        <div class="text-xs text-gray-500">Experience</div>
                    </div>
                    <div class="text-center">
                        <div class="font-medium text-gray-700">{entry.value}</div>
                        <div class="text-xs text-gray-500">Value</div>
                    </div>
                    <div class="text-center">
                        <div class="font-medium text-gray-700">{entry.mood:.1f}</div>
                        <div class="text-xs text-gray-500">Mood</div>
                    </div>
                </div>
                {notes_html}
                {images_html}
            </div>
            """
        
        html_content = f"""
        <div class="space-y-4">
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-lg font-semibold text-gray-800">Restaurant History ({len(entries)} entries)</h3>
                <div class="flex gap-2">
                    <button hx-get="/history?sort_by=date" hx-target="#history-content" 
                            class="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 {'bg-blue-200' if sort_by == 'date' else ''}">
                        Sort by Date
                    </button>
                    <button hx-get="/history?sort_by=score" hx-target="#history-content"
                            class="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 {'bg-blue-200' if sort_by == 'score' else ''}">
                        Sort by Score
                    </button>
                </div>
            </div>
            {entries_html}
        </div>
        """
    
    return HTMLResponse(content=html_content)

# Health check endpoint
@app.get("/health")
def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 