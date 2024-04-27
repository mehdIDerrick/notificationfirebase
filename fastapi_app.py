
import logging
from fastapi import FastAPI, HTTPException, Body, Request,Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from firebase_admin import credentials, initialize_app, messaging
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv
logging.basicConfig(level=logging.DEBUG)
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Load environment variables from .env file
load_dotenv()

# Firebase Admin SDK setup (use environment variables)
cred = credentials.Certificate({
  "type": "service_account",
  "project_id": os.getenv("FIREBASE_PROJECT_ID"),
  "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
  "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
  "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
  "client_id": os.getenv("FIREBASE_CLIENT_ID"),
  "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
  "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
  "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
  "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
  "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN")  # Assuming you added this in your .env file
})

firebase_app = initialize_app(cred)

uri = os.getenv("MONGODB_URI")
# MongoDB Connection URI
client = MongoClient(uri)

# Test the connection

db = client["my_orange"]  # Remplacez "your_database_name" par le nom de votre base de données MongoDB
tokens_collection = db["user_orange"] 
messages_collection = db["sent_messages"]  # Nouvelle collection pour stocker les messages envoyés
class TokenData(BaseModel):
    phone: str
    token: str

def insert_sent_message(phone: str, title: str, body: str, token: str = "", status: str = "0"):
    messages_collection.insert_one({
        "phone": phone,
        "title": title,
        "body": body,
        "token": token,
        "status": status
    })
def upsert_token(phone, token):
    tokens_collection.update_one(
        {"phone": phone},
        {"$set": {"token": token}},
        upsert=True
    )

@app.post("/register-token/")
async def register_token(token_data: TokenData):
    try:
        upsert_token(token_data.phone, token_data.token)
        return {"success": True, "message": "Token and phone number registered/updated successfully."}
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Failed to update database.")

@app.post("/send-notification-firebase/")
async def send_notification_firebase(phone: str = Form(...), title: str = Form(...), body: str = Form(...)):
    try:
        # Rechercher le document de l'utilisateur et vérifier le statut
        message_document = messages_collection.find_one({"phone": phone, "title": title, "body": body})
        if message_document and message_document['status'] == 1:
            return {"error": "Notification sending is disabled for this message"}

        token_document = tokens_collection.find_one({"phone": phone})
        if token_document:
            print("token user", token_document['token'])
            message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                token=token_document['token']
            )
            response = messaging.send(message)
            # Mise à jour du document du message avec le statut envoyé (peut-être définir à 0 ou 1 selon la logique d'entreprise)
            messages_collection.update_one(
                {"phone": phone, "title": title, "body": body},
                {"$set": {"status": 1}},  # Supposons que 0 signifie 'envoyé avec succès'
                upsert=True  # Insère le document si non trouvé
            )
            return {"success": True, "message": f"Notification sent to {phone}. Response: {response}"}
        else:
            return {"error": "No token found for given phone number"}

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    
@app.post("/insert-message/")
async def insert_message(phone: str = Form(...), title: str = Form(...), body: str = Form(...)):
    try:
        # Vérifier si le téléphone est valide (vous pouvez ajouter plus de validation si nécessaire)

        # Insérer le message dans MongoDB
        insert_sent_message(phone, title, body)  # Vous pouvez laisser le token vide pour un message non envoyé
        
        return {"success": True, "message": f"Message inserted for {phone}."}
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/view-messages/", response_class=HTMLResponse)
async def view_messages(request: Request):
    messages = list(messages_collection.find())
    return templates.TemplateResponse("messages_list.html", {"request": request, "messages": messages})


@app.get("/send-form/", response_class=HTMLResponse)
async def send_form(request: Request):
    phones = [doc['phone'] for doc in tokens_collection.find({}, {"phone": 1})]
    return templates.TemplateResponse("send_form.html", {"request": request, "phones": phones})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
