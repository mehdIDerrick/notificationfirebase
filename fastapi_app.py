from fastapi import FastAPI, HTTPException, Body,UploadFile, File
from firebase_admin import credentials, initialize_app, messaging
from pydantic import BaseModel
import csv
app = FastAPI()

class TokenData(BaseModel):
    token: str

# Chemin vers votre fichier clé JSON de Firebase
cred_path = 'google-services.json'
cred = credentials.Certificate(cred_path)
firebase_app = initialize_app(cred)

@app.post("/register-token/")
async def register_token(token_data: TokenData):
    token = token_data.token
    print(f"Token reçu : {token}")
    
    # Écrire le token dans un fichier CSV
    with open('tokens.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([token])

    return {"success": True, "message": "Token enregistré avec succès."}

@app.post("/send-notification/")
async def send_notification(title: str, body: str):
    try:
        # Ouvrir le fichier CSV et récupérer les tokens
        with open('tokens.csv', mode='r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                token = row[0]  # Supposant que le token est dans la première colonne

                # Créer un message avec le token actuel
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=body,
                    ),
                    token=token,
                )

                # Envoyer la notification
                response = messaging.send(message)
                print(f"Notification sent to token {token}: {response}")

        return {"success": True, "message": "Notifications sent successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))