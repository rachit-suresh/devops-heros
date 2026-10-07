from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

from .database import get_db, Base, engine
from .models import Album
from .schemas import AlbumCreate, AlbumUpdate, AlbumOut

REQUEST_COUNT = Counter("tracktonic_http_requests_total", "HTTP requests", ["method", "endpoint", "status"])
REQUEST_LATENCY = Histogram("tracktonic_http_request_duration_seconds", "Request latency", ["endpoint"])

app = FastAPI(title="TrackTonic", version="1.0.0", description="Music listening tracker - log albums, rate them, keep a queue")

@app.middleware("http")
async def metrics_middleware(request, call_next):
    start = time.time()
    response = await call_next(request)
    endpoint = request.url.path
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(time.time() - start)
    REQUEST_COUNT.labels(method=request.method, endpoint=endpoint, status=response.status_code).inc()
    return response

@app.get("/health")
def health():
    return {"status": "ok", "app": "tracktonic"}

@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    return PlainTextResponse(generate_latest().decode(), media_type=CONTENT_TYPE_LATEST)

@app.get("/api/albums", response_model=list[AlbumOut])
def list_albums(status: str | None = None, db: Session = Depends(get_db)):
    q = db.query(Album)
    if status:
        q = q.filter(Album.status == status)
    return q.order_by(Album.created_at.desc()).all()

@app.post("/api/albums", response_model=AlbumOut, status_code=201)
def create_album(payload: AlbumCreate, db: Session = Depends(get_db)):
    album = Album(title=payload.title, artist=payload.artist, year=payload.year, status="queued")
    db.add(album)
    db.commit()
    db.refresh(album)
    return album

@app.get("/api/albums/{album_id}", response_model=AlbumOut)
def get_album(album_id: int, db: Session = Depends(get_db)):
    album = db.get(Album, album_id)
    if not album:
        raise HTTPException(404, "album not found")
    return album

@app.put("/api/albums/{album_id}", response_model=AlbumOut)
def update_album(album_id: int, payload: AlbumUpdate, db: Session = Depends(get_db)):
    album = db.get(Album, album_id)
    if not album:
        raise HTTPException(404, "album not found")
    if payload.rating is not None:
        album.rating = payload.rating
        album.status = "listened"
    if payload.status is not None:
        album.status = payload.status
    db.commit()
    db.refresh(album)
    return album

@app.delete("/api/albums/{album_id}", status_code=204)
def delete_album(album_id: int, db: Session = Depends(get_db)):
    album = db.get(Album, album_id)
    if not album:
        raise HTTPException(404, "album not found")
    db.delete(album)
    db.commit()

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
