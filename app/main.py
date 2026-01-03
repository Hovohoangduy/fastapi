from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from typing import Optional, List
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

@app.post("/createposts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    # post_dict = new_post.model_dump()
    # post_dict['id'] = randrange(0, 1000000)
    # my_post.append(post_dict)
    
    ### raw SQL
    # cursor.execute("""
    #                INSERT INTO posts (title, content, published) 
    #                VALUES (%s, %s, %s) 
    #                RETURNING * 
    #                """,
    #                (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()

    new_post = models.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

@app.get("/posts/latest")
def post_latest():
    post = my_post[len(my_post) - 1]
    return {"detail": post}

@app.get("/posts/{id}", response_model=List[schemas.Post])
def get_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts WHERE id = %s """, (str(id)))
    # test_post = cursor.fetchone()
    # print(test_post)

    # post = find_post(id)
    # if not post:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #                         detail=f"post with {id} was not found")
    #     # respone.status_code = status.HTTP_404_NOT_FOUND
    #     # return {"message": f"post with {id} was not found"}
    # print(post)
    post = db.query(models.Post).filter(models.Post.id == str(id)).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with {id} was not found")
        # respone.status_code = status.HTTP_404_NOT_FOUND
        # return {"message": f"post with {id} was not found"}
    print(post)
    # return {"post_detail": post}
    return post

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def detete_post(id: int, db: Session = Depends(get_db)):
    ### raw SQL
    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id),))
    # deleted_post = cursor.fetchone()
    # conn.commit()

    post = db.query(models.Post).filter(models.Post.id == str(id))

    # index = find_index_post(id)
    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")
    # my_post.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}", response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db)):
    ### raw SQL
    # cursor.execute(""" UPDATE posts SET title = %s, content = %s, published = %s 
    #                WHERE ID = %s
    #                RETURNING *
    #                """,
    #                (post.title, post.content, post.published, str(id)))
    # updated_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    # index = find_index_post(id)
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")
    
    post_query.update(updated_post.model_dump(), synchronize_session=False)
    db.commit()
    # post_dict = post.model_dump()
    # post_dict['id'] = id
    # my_post[index] = post_dict
    # return {"data": post_query.first()}
    return post_query.first()


@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_users(user: schemas.UserCreate, db: Session = Depends(get_db)):
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
