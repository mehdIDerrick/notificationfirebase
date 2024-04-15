import os
from fastapi import FastAPI, HTTPException, Body, UploadFile, File
from firebase_admin import credentials, initialize_app, messaging
from pydantic import BaseModel
import csv
from waitress import serve

app = FastAPI()

class TokenData(BaseModel):
    token: str

# Use environment variables for Firebase credentials
cred = credentials.Certificate({
  "type": "service_account",
  "project_id": "orangetunisie-4ae1c",
  "private_key_id": "2e91bac2601fd69f1e61778edb77f5e667068bab",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDSXBFCy90jHu0F\nZd9RyFPzGGLF1xwJf8QQkre4A/OI6vJJMksluLM53WgFInXcln4SQ9fSnNEEKhl6\n0z4H9++iW79DG1tuEjONNCToUq3vDgIm8xQD1jUefvrcQyhjATmsiph7v25d2vad\nNC23t37E8WxoI3tXbxAttOtJV6atAhMdGYgDi+jOj24GJKCg3f5WFFCCXCL7zNDv\nE2FVf4lB1eK7p4WfeE0mIZOwgSpYTc95soHTKieyp/vBFPGd3KmFvlipyhnpKFx3\nL5iDl5KvlIEGyqMV6Iu1ImBLvSy4pTH3X3jsWCvJycLmhbzOi86oxmZ/qcl3eMj6\nplnG4KYvAgMBAAECggEAB9umlo8wbkXcL+3cteXPIrhQDfjCtFwiwiDfzFM849e/\niPXgJHopZFvUiMbaoIy5ecKfUARb6ed7jZxRFVGw/l+BlNSYEsGLBOBR7KDvwPlX\nIc/qeQ9cazES1savdRtUwOxFC/ATKF4Zu/+darp6MIoLosw/X7QL+M/7LzhV/gXa\n4RwmuaQuf1FUfI6LlQsrXJek1Rxl7K8wdtBdLH7pyyU6I6h6l83KC4A4wpm3tALY\n0E0/JrflGTNquPcY3QE6pqwTYwosMRT+EROfZ5qaffvgxcX5vE3ikugtLkKFXQum\nLn+Ka3HwH0lw324OgxHfeaGpVuW8zwUHWWG3OwrgmQKBgQD12494xtwcWaIdFggd\nenF4NE3o6UlqDJFHfKkG8seFP2um2Q0exOBQokgxdf2JVbJPy0K5ejDcE5Hi1vqv\nAqAMBOoJgb+mGTQq3pg4zpS+5YOnNOjS8bd+scEIIVFte9RTRukrza0RCy9UKPyA\nv8Vk6djyvP+6rI6HLORVl56cUwKBgQDbCZ8cLjTH8+/NLYUclLm2minOMN5Mug4E\n1o0C81+f4snD7TRcZbSMr3iswpVQbkVd+suuaweQ2d/7vpsTyyogqHmB2GuSpgRy\nNmdPttUqV0j0iU7ALDz/2CUHXOYxJMdUkWtQrTfmUSZy5E8GjMkLhWpLtjZnvx2i\n9xnGf8tzNQKBgDTRASZiGiEhBFmZRQ8IId4/5kjV7QaSQpeH6Uvr1f8DG95RHKdy\nhfnskvPFND1PoqnPsbrkzCBLN/jyVBJKzxUl7R0zuXc2TOW0wiDaCExmQ/0kuauv\nb8sQ5rYXakXJ51gokKjvW3Gg5H8A+xWxnPdL4WZsQcfZkBjsBPV6SAGvAoGAeldU\nbIwOZQSGE0byi3UyiaBv6z/2WkqtW9xuZJCE/6vPYETUMyuHffDgaTZB6eu9iPF0\n5JXZYvmelmDvA0492IHhZDn6U62w3A4xBCAtzfl0wUkUGFhdNdWHUSZ9WEOfpkeW\n9jfZ+iWnYRLOZO0rueip52H931Kq/gQgfHOSsmUCgYBaqRA7oKUcenhOFR+LDEPb\nFUg7uI+ksWMphkvFq58H5jhiB/5zfJfqh2AluWG/AkWCNahLGeg/MhWPYt9aXvAB\n6aFoQhH2RDrX6fbAY2du3I6fZdjHDr8w2Lk01J1j6ySA7t9GeR1wCrbmfvq8jQ5s\npBl1Ei2P0IZbRt+EOCaZIA==\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-mqrp9@orangetunisie-4ae1c.iam.gserviceaccount.com",
  "client_id": "103304431877193384786",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-mqrp9%40orangetunisie-4ae1c.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
})

 

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

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)
