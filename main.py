from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    number: int
    published: bool = True
    rating: Optional[float] = None

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

@app.get("/posts")
def get_post():
    return {"data": my_post}

@app.post("/createposts", status_code=status.HTTP_201_CREATED)
def create_posts(new_post: Post):
    post_dict = new_post.model_dump()
    post_dict['id'] = randrange(0, 1000000)
    my_post.append(post_dict)
    return {"message": post_dict}

@app.get("/posts/latest")
def post_latest():
    post = my_post[len(my_post) - 1]
    return {"detail": post}

@app.get("/posts/{id}")
def get_post(id: int, respone: Response):
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with {id} was not found")
        # respone.status_code = status.HTTP_404_NOT_FOUND
        # return {"message": f"post with {id} was not found"}
    print(post)
    return {"post_detail": post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def detete_post(id: int):
    index = find_index_post(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")
    my_post.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    index = find_index_post(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")
    post_dict = post.model_dump()
    post_dict['id'] = id
    my_post[index] = post_dict
    return {"data": post_dict}