from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from auth import create_access_token, get_current_user, verify_password, FAKE_USERS
import models

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI()


# Pydantic schema for request body
class ItemSchema(BaseModel):
    name: str
    price: float
    in_stock: bool = True


# Dependency — opens a DB session per request, closes it after
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# LOGIN
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = FAKE_USERS.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": form_data.username})
    return {"access_token": token, "token_type": "bearer"}


# CREATE
@app.post("/items")
def create_item(item: ItemSchema, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    db_item = models.Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


# READ ALL
@app.get("/items")
def list_items(db: Session = Depends(get_db)):
    return db.query(models.Item).all()


# READ ONE
@app.get("/items/{item_id}")
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


# UPDATE
@app.put("/items/{item_id}")
def update_item(item_id: int, item: ItemSchema, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in item.model_dump().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item


# DELETE
@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"message": f"Item {item_id} deleted"}
