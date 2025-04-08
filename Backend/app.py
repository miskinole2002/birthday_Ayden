from fastapi import FastAPI,Request,Form
import uvicorn
import os, sys
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
app=FastAPI()


templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "templates"))
templates=Jinja2Templates(directory=templates_dir)
#static
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "static"))
app.mount("/static", StaticFiles(directory=static_dir))

users = {"admin": "1234"}

@app.get("/")
async def home_page(resquest:Request):
    token=resquest.cookies.get("Authorization")
    if token=="Bearer Token":

        return templates.TemplateResponse("home.html",{"request":resquest ,"username":True})   
    return templates.TemplateResponse("home.html",{"request":resquest ,"username":False}) 
@app.get("/login")
async def login_page(resquest:Request): 
    return templates.TemplateResponse("login.html",{"request":resquest})

@app.post("/login")
async def login_page(username: str = Form(...), password: str = Form(...)): 
    if username in users and users[username] == password:
       
        response = RedirectResponse(url='/', status_code=302)
        response.set_cookie(key="Authorization", value="Bearer Token", httponly=True)
        print(response)
        return response
    return templates.TemplateResponse("login.html",{"request":Request})

@app.get("/about")
async def about(resquest:Request):
   token=resquest.cookies.get("Authorization")
   if token=="Bearer Token":

        return templates.TemplateResponse("about.html",{"request":resquest ,"username":True})   
   return templates.TemplateResponse("about.html",{"request":resquest ,"username":False}) 

@app.get("/commentaire")
async def commentaire(resquest:Request):
   token=resquest.cookies.get("Authorization")
   if token=="Bearer Token":

        return templates.TemplateResponse("commentaire.html",{"request":resquest ,"username":True})   
   return templates.TemplateResponse("commentaire.html",{"request":resquest ,"username":False}) 

@app.get("/logout")
async def logout():
    response = RedirectResponse(url='/login')
    response.delete_cookie('Authorization')
    return response

if __name__=="__main__":
    uvicorn.run(app,host='0.0.0.0', port=8002, workers=1)