import os.path
import streamlit as st

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import json

        
def save_files(user_id, file_name):
    SCOPES = ["https://www.googleapis.com/auth/drive"]
    creds = None
    if not os.path.exists("token.json"):
        token = json.loads(st.secrets["GDRIVE_TOKEN"].replace("'", "\""))
        with open("token.json", "w") as f:
            json.dump(token, f)
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)


    try:
        # create drive api client
        service = build("drive", "v3", credentials=creds)


        folder_name = user_id 
        parent_folder_id = "1zuSXfQiKiCkqJvP7CWZ3C4Ed0gIuYwew"
        folder_id = create_folder(service, folder_name, parent_folder_id)
        file_metadata = {"name": file_name, "parents": [folder_id]}
        media = MediaFileUpload(file_name, mimetype="application/json")
        # pylint: disable=maybe-no-member
        file = (
            service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )
        print(f'>> File ID: {file.get("id")}')

    except HttpError as error:
        print(f">> An error occurred: {error}")
        file = None

        


def create_folder(service, folder_name, parent_folder_id):
    # First, check if the folder already exists
    query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}'"
    if parent_folder_id:
        query += f" and '{parent_folder_id}' in parents"
    
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    folders = results.get('files', [])

    if folders:
        # Folder exists, return its ID
        print(f">> Folder already exists: {folders[0]['id']}")
        return folders[0]['id']
    else:
        # Folder doesn't exist, create it
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_folder_id:
            folder_metadata['parents'] = [parent_folder_id]
        
        folder = service.files().create(body=folder_metadata, fields='id').execute()
        print(f">> Generated new folder: {folder.get('id')}")
        return folder.get('id')