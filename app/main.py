from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from . import models
from .database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Post(BaseModel):
    title: str
    content: str
    # number: int
    published: bool = True
    rating: Optional[float] = None

try:
    conn = psycopg2.connect(host='localhost', 
                            database='mydb', 
                            user='root', 
                            password=123456, 
                            cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    print('DB connection was succesfull!')
except Exception as error:
    print("Connecting DB to failed!")
    print("Error: ", error)
    time.sleep(2)

my_post = [{"title": "title of 1", "content": "content of 1", "id": 1}, {"title": "title of 2", "content": "content of 2", "id": 2}]

def find_post(id):
    for p in my_post:
        if p['id'] == id:
            return p
def find_index_post(id):
    for i, p in enumerate(my_post):
        if p['id'] == id:
            return i


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"data": posts}

@app.get("/posts")
def get_post():
    cursor.execute("""SELECT * FROM posts """)
    posts = cursor.fetchall()
    print(posts)
    return {"data": posts}

@app.post("/createposts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    # post_dict = new_post.model_dump()
    # post_dict['id'] = randrange(0, 1000000)
    # my_post.append(post_dict)
    cursor.execute("""
                   INSERT INTO posts (title, content, published) 
                   VALUES (%s, %s, %s) 
                   RETURNING * 
                   """,
                   (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()

    return {"message": new_post}

@app.get("/posts/latest")
def post_latest():
    post = my_post[len(my_post) - 1]
    return {"detail": post}

@app.get("/posts/{id}")
def get_post(id: str):
    cursor.execute("""SELECT * FROM posts WHERE id = %s """, (str(id)))
    test_post = cursor.fetchone()
    print(test_post)
    # post = find_post(id)
    # if not post:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #                         detail=f"post with {id} was not found")
    #     # respone.status_code = status.HTTP_404_NOT_FOUND
    #     # return {"message": f"post with {id} was not found"}
    # print(post)
    return {"post_detail": test_post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def detete_post(id: int):
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id),))
    deleted_post = cursor.fetchone()
    conn.commit()
    # index = find_index_post(id)
    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")
    # my_post.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute(""" UPDATE posts SET title = %s, content = %s, published = %s 
                   WHERE ID = %s
                   RETURNING *
                   """,
                   (post.title, post.content, post.published, str(id)))
    updated_post = cursor.fetchone()
    conn.commit()
    # index = find_index_post(id)
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")
    # post_dict = post.model_dump()
    # post_dict['id'] = id
    # my_post[index] = post_dict
    return {"data": updated_post}