import os
from fastapi import FastAPI, HTTPException, Body, UploadFile, File
from firebase_admin import credentials, initialize_app, messaging
from pydantic import BaseModel
import csv
from waitress import serve
import uvicorn
app = FastAPI()

class TokenData(BaseModel):
    phone: str
    token: str

# Use environment variables for Firebase credentials
cred = credentials.Certificate({
  "type": "service_account",
  "project_id": "my-dash-a67f9",
  "private_key_id": "946023728439248710cc8c4d076c92a90e32cb31",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDYuUZRp5AryhV8\nxOriFJ1sAEYWkK7cjNkUYg5c6W3RQYAEGnu88shV5gHAmRbQH5sRgBJL0ixjTZiB\n8rC/WrTYqKCxnTMzoLzgV/ofI+xfhwvUop1IqEnup4gHFefTSmvsXZ9JcrOEsM+H\nlMSEtj77g3Y6IA8loGbIBJwCNldtynVjCTR/kNyVRjKNvTCEKr1+vkLyMcjG7zVE\nh0ORaAGNVgBjzyrOjT+H3bQG0wNHoB+p+p38cKAkiOf4/s1RrWdDxFKcC/7DR5M7\njDxGPIny9XJnljGVsJGAQrAiRAwDmRYYMhKhRfCvNmlzB9tqNpKy972/YZ7Qdsnw\nCCR/6p2VAgMBAAECggEAGgQPrsCnJrfhDB5qtc3/YcDHU8Z1fztB2de1iANrhTml\nf5ia7wEpTwpyfmds3M9WeEDVXBhe72LCt81lg0BabOxn3I/ANDvg6ytpy/AuMVTO\n9O0Pusec7GhcWha6mAYbM39qSNEF6hv8JaHpqfwN+SJRqxjrHeYF6zqGbHY6g47C\nuBP955svNBq3OeHU2B8OEIRwPKcx56ngd9SHhOwD6ErEsp9s/HHQk67XzLGyH6Sx\ntFQePAXM421zXZOSIFjNQ16BhVhfnogfHmKz/9X1GXz56l9Sb67TvHLcxXXr8gSu\n2rFyplxhjRd727YqHDleKVJuQ5xCNXu9NQ2AtF9jVwKBgQD7KCLk67XZXGdq+2jM\nYwCF/E+nImMjqB9XyN3BaJL8xqZB5bTEzpot11xcNi+zoR6d4WYMQFKnMJ7dw0Xr\nnlaDLiqUMW+kICUCmwou4Z43+iMUNb5fIsB0syM9IEbjpXD5OqTiGj/oj+22Sbl/\nu5h+zzG8imrU72ohLwmasL3zfwKBgQDc5yfeiOceTBDzjrc/I2AhTGNQdjGETt1l\nzGqaIefDEppM5d7BAicGQGrXi5qUenfwjMsWqEshZf1Pe1rncPAWTgWpcZKIkMel\n2pfED+xAO9z351yFsRCpLpgYmxAkgLzIX4YgxJP1iYK7T8+2LijxFk44ltKkZqwn\nm7I+n5/o6wKBgHAHgjEclvwCxLqqtB9fFc+uMRV7OD+icYClv4zTCaWpMmX4gX68\nLXe/NZqILRTyDIceEHfshTHAdUy0Gs8zzKEtCZ8awhKyp++Wmp840mtjrxwHsQgc\npz4m3dQZPqWymUcCiqO0U8d30+/YyN6aHjaKU0QndenPdUaiBaWzqrcfAoGBAK2/\nVrmO3pIS7EZVW0Za8bJfHcJcpIfXbAY0qShAQMVLLXgMWY9fvQgKxL5yfIwKY6od\nY2OXzTgguwO4F4DwcLZqecOTo9isX4vRCgvZJk5Dh4KpRDmXUm5vSowX8rNzWokT\nsTC2zVWT6fKgTNSTK/qsO6wA3P8YDpI8wQ7GiIUvAoGBAJHdgGia9OGIbBXtyqUF\nJFZEwqR9CCogunWOr9XlyAUZ9RD4OhZnOkxXzOwS/ptg/MoMKBK2BcXYibLbiOiV\nWaEEBOzCXrE0LQi/zTkDqIlGD9YWNLv2T4Qw3AXyHANcct2y5JAaIrFSqdNs+oyz\nUUirDlEstmMVer/e7FD621AK\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-7o5xg@my-dash-a67f9.iam.gserviceaccount.com",
  "client_id": "110916257392787033128",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-7o5xg%40my-dash-a67f9.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
})

 

firebase_app = initialize_app(cred)

@app.post("/register-token/")
async def register_token(token_data: TokenData):
    phone = token_data.phone
    token = token_data.token
    print(f"Phone: {phone}, Token: {token}")

    # Read existing data
    existing_tokens = []
    try:
        with open('tokens.csv', mode='r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                existing_tokens.append(row)
    except FileNotFoundError:
        # File not found is okay, will create later
        pass

    # Check if phone number already exists
    for i, row in enumerate(existing_tokens):
        if row[0] == phone:
            # Phone number already exists, update token
            existing_tokens[i][1] = token
            break
    else:
        # Phone number does not exist, add new entry
        existing_tokens.append([phone, token])

    # Write updated data to CSV file
    try:
        with open('tokens.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(existing_tokens)
        return {"success": True, "message": "Token and phone number registered/updated successfully."}
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Failed to write to file.")
    
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
    uvicorn.run(app, host="0.0.0.0", port=8000)
