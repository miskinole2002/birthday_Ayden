from fastapi import FastAPI,Request,Form
import uvicorn
import os, sys
import  snowflake.connector as sc 
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from .Functions import password_hash,password_verify
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
app=FastAPI()
load_dotenv()
app.add_middleware(SessionMiddleware,secret_key=os.getenv("secret_key") , max_age=60)

templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "templates"))
templates=Jinja2Templates(directory=templates_dir)
#static
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "static"))
app.mount("/static", StaticFiles(directory=static_dir))


Connect= sc.Connect(
    user= os.getenv("snowflake_user"),
    password= os.getenv("snowflake_password"),
    account=os.getenv("snowflake_account"),
    database=os.getenv("snowflake_database"),
 

    )   

cursor=Connect.cursor() # pour manager toutes les functions lies a la base de donnes

@app.get("/")
async def home_page(request:Request):
    user = request.session.get("user")
    if user:

        return templates.TemplateResponse("home.html",{"request":request ,"username":user})   
    return templates.TemplateResponse("home.html",{"request":request }) 
@app.get("/login")
async def login_page(request:Request): 
    error=request.session.get("error",None)
    if error:
        print(error)
        return templates.TemplateResponse("login.html",{"request":request,"error":error})
    return templates.TemplateResponse("login.html",{"request":request})

@app.post("/login")
async def login_page(request:Request,username: str = Form(...), password: str = Form(...)): 
    sql= "SELECT * from  Ayden.Ayd.Users where Email=%s"
    params=[username]
    cursor.execute(sql,params)
    resultat=cursor.fetchone()
    if resultat :
      x= password_verify(password,resultat[3])

      if x :
          r={
              "nom":resultat[1],
              "prenom":resultat[2],
              "Email":resultat[3]
          }
          response = RedirectResponse(url='/', status_code=302)
          
          request.session["user"] = r

          return response
      else:
          request.session["error"] = "mot de passe incorrect"
          
          return RedirectResponse(url='/login', status_code=302)
      
    else: 
        request.session["error"] = "email introuvable "

        return RedirectResponse(url='/login', status_code=302)




@app.get("/about")
async def about(request:Request):
    user = request.session.get("user")
    if user:

        return templates.TemplateResponse("about.html",{"request":request ,"username":user})   
    return templates.TemplateResponse("about.html",{"request":request }) 

@app.get("/commentaires")
async def commentaire(request:Request):
    user = request.session.get("user")
    sql= "SELECT * from  Ayden.Ayd.COMMENTAIRES "
    cursor.execute(sql)
    resultat=cursor.fetchall()
    response=[]
    for row in resultat:
        result={
            "nom":row[1],
            "commentaire":row[2]
        }

        response.append(result) 

    
    if user:

        return templates.TemplateResponse("commentaire.html",{"request":request ,"username":user, "response":response})   
    return templates.TemplateResponse("commentaire.html",{"request":request,"response":response }) 

@app.post("/commentaires")
async def commentaire(request:Request, username: str = Form(...), commentaire: str = Form(...)):

    sql= """ INSERT INTO Ayden.Ayd.commentaires(Nom,commentaire)
       values (%s,%s) """
    params=[username,commentaire]
    cursor.execute(sql,params) 
   
    
    return RedirectResponse(url='/commentaires', status_code=302)


@app.get("/adduser")
async def adduser(request:Request):
    user = request.session.get("user")
    message=request.session.pop("message",None)
    if user :

        return templates.TemplateResponse("userAdd.html",{"request":request ,"username":user,"message":message})  
    return templates.TemplateResponse("home.html",{"request":request }) 

@app.post("/adduser") 
async def adduser( request:Request ,nom: str = Form(...), prenom: str = Form(...),username: str = Form(...), password: str = Form(...)):
   
   sql = "SELECT * FROM Ayden.Ayd.Users where Email=%s"
   params=[username]
   cursor.execute(sql,params)
   resultat=cursor.fetchone()
    

   if resultat : 
        request.session["message"] = f"{username} est deja associe a un compte  "
        
        
        return  RedirectResponse(url='/adduser', status_code=302)
    
   else :
        
       y= password_hash(password)
       sql =""" 
       
       INSERT INTO Ayden.Ayd.Users(Nom,Prenom,password,Email)
       values (%s,%s,%s,%s)
       
       """

       params=[nom,prenom,y,username]
       x=cursor.execute(sql,params)
       request.session["message"] =  f"{nom} {prenom} a ete bien ajoute "


       return RedirectResponse(url='/adduser', status_code=302)
    






@app.get("/logout")
async def logout(request:Request):
    response = RedirectResponse(url='/login')
    request.session.clear()
    return response

if __name__=="__main__":
    uvicorn.run(app,host='0.0.0.0', port=8002, workers=1)

   

