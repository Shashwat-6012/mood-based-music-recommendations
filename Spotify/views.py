from django.shortcuts import render,  redirect
from django.shortcuts import HttpResponse
import requests
import base64
import json
from deepface import DeepFace
import cv2
import dlib
import imutils
from imutils import face_utils
from imutils.video import VideoStream
from imutils.face_utils import FaceAligner
from rest_framework.response import Response
import numpy as np
from rest_framework.decorators import api_view
# from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer

@api_view(('GET','POST'))
# @renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def Home(request):
    if request.method == 'GET':
        vs = VideoStream(src=0).start()
        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor(
            'face_Data/shape_predictor_68_face_landmarks.dat')
        fa = FaceAligner(predictor, desiredFaceWidth=96)
        listmood = []
        while True:
            test_img = vs.read()
            test_img = imutils.resize(test_img, width=800)
            gray = cv2.cvtColor(test_img, cv2.COLOR_BGR2GRAY)
            faces = detector(gray, 0)
            for face in faces:
                print("inside for loop")
                (x, y, w, h) = face_utils.rect_to_bb(face)

                face_aligned = fa.align(test_img, gray, face)
                # Saving the image dataset, but only the face part, cropping the rest

                if face is None:
                    print("face is none")
                    continue
                listmood.append(test_img)
                face_aligned = imutils.resize(face_aligned, width=400)
                cv2.rectangle(test_img, (x, y), (x+w, y+h), (0, 255, 0), 1)

                cv2.imshow("Add Images", test_img)
                cv2.waitKey(1)
            if 0xFF == ord('q') or len(listmood) > 50:
                break
        vs.stop()
        cv2.destroyAllWindows()
        obj = DeepFace.analyze(img_path=listmood[3], actions=[
                               'emotion'], enforce_detection=False)
        # destroying all the windows
        print(obj)
        
    
        client_id = "f8ad59ad353f4c99bce1e6e296e20ff6"
        client_secret = "f2a7160da48a44fe9e02cdd1f6c79722"

        def get_token():
            auth_string = client_id + ":" + client_secret
            auth_bytes = auth_string.encode('utf-8')
            auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

            url = "https://accounts.spotify.com/api/token"
            headers = {
                "Authorization" : 'Basic ' + auth_base64,
                "Content-type" : "application/x-www-form-urlencoded"
            }
            data = {"grant_type": "client_credentials"}
            result = requests.post(url, headers=headers, data=data)
            json_results = json.loads(result.content)     # converts json string into python dictionary.
            token = json_results['access_token']
            return token

        def get_auth_header(token):
            return {"Authorization": "Bearer " + token}
        
        def get_playlist(genre, token):
            type = "Bollywood"  # Bollywood ya Hollywood type of music Enter.
            artist = "Arijit singh"   # Enter Specific artist name. if any.  
            url = "https://api.spotify.com/v1/search"
            query = f"?q={type}artist:{artist}genre:{genre}&type=track&limit=20&market=IN"
            header = get_auth_header(token)
            query_url = url + query
            result = requests.get(query_url, headers=header)
            data = json.loads(result.content)
            if len(data) == 0:
                return "No Genres matched the name"
            else:
                return data['tracks']['items']

        token = get_token()
        if obj[0]['dominant_emotion'] == 'angry':
            playlist = get_playlist('Hip hop', token)
            return Response(playlist)
        elif obj[0]['dominant_emotion'] == 'sad':
            playlist = get_playlist('Lo-fi', token)
            return Response(playlist)
        elif obj[0]['dominant_emotion'] == 'happy':
            playlist = get_playlist('jazz', token)
            return Response(playlist)
        elif obj[0]['dominant_emotion'] == 'neutral':
            playlist = get_playlist('Bollywood', token)
            return Response(playlist)
        

    elif request.method == 'POST':
        name = request.form['name']
        return f'Hello, {name}!'

    return render(request, 'Spotify/home.html')

def Search(request):
    if(request.method == "POST"):
        name  = request.POST.get('name')
        country = request.POST.get('country')
    client_id = "f8ad59ad353f4c99bce1e6e296e20ff6"
    client_secret = "f2a7160da48a44fe9e02cdd1f6c79722"

    def get_token():
        auth_string = client_id + ":" + client_secret
        auth_bytes = auth_string.encode('utf-8')
        auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

        url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization" : 'Basic ' + auth_base64,
            "Content-type" : "application/x-www-form-urlencoded"
        }
        data = {"grant_type": "client_credentials"}
        result = requests.post(url, headers=headers, data=data)
        json_results = json.loads(result.content)     # converts json string into python dictionary.
        token = json_results['access_token']
        return token

    def get_auth_header(token):
        return {"Authorization": "Bearer " + token}

    def get_artist(artist_name, token):
        url = "https://api.spotify.com/v1/search"
        query = f"?q={artist_name}&type=artist&limit=1"
        header = get_auth_header(token)
        query_url = url + query
        result = requests.get(query_url, headers=header)
        data = json.loads(result.content)
        if len(data) == 0:
            return "No artist matched the name"
        else:
            return data['artists']['items'][0]
        
    def get_tracks(token, artist_id):
        url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country="+country
        header = get_auth_header(token)
        result = requests.get(url, headers=header)
        data = json.loads(result.content)['tracks']
        return data

    token = get_token()
    print(token)

    artist = get_artist(name, token)
    artists_id = artist['id']
    songs = get_tracks(token, artists_id)
    # print(songs)
    song_names = []

    for idx, song in enumerate(songs):
        song_names.append(f"{song['preview_url']}")
    
    params = {'name': name, 'songs': song_names}
    
    return render(request, 'Spotify/result.html', params)