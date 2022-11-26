import requests
import time
from datetime import datetime
import json
from flask import Flask,redirect,request,render_template



### variables 
clientId = ''
clientSecret = ''
urlRedirect =  'http://eba77.com:5000/callback'
urlAuthToken = 'https://www.linkedin.com/oauth/v2/accessToken'
urlGetMe = 'https://api.linkedin.com/v2/me?projection=(id,firstName,lastName,profilePicture(displayImage~:playableStreams))'
urlGetMeEmail = 'https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))'
urlPostMessage = 'https://api.linkedin.com/v2/ugcPosts'

app = Flask(__name__)


### respuestas de navegacion

@app.route('/') # pagina eba77:5000 (home) 
def index():
    return render_template('index.html') 

@app.route('/callback') # pagina eba77:5000/callback 
def callback(): #la función se llama igual que el route y dirige a ella directamente 
    args = request.args #no tiene status_code (no es una petición sino la redirección)
    authCode = args.get("code") #code de autenticacion de permisos del usuario
    global tokenInfo #guardar la autenticacion para poder usarla en los metodos rest
    tokenInfo = gettoken(authCode) #token de autenticacion de la aplicacion con el scope ya aplicado
    if tokenInfo == -1:
        return render_template('error.html')
    else:
        print (tokenInfo[0])
        return redirect('/myinfo') #redirigir automaticamente al render que saca la informacion del usuario y que no de error si se recarga la pagina (el code expiora en 50 seg e iría en la misma url)

@app.route('/myinfo')
def myinfo():
    meInformation = getme(tokenInfo[0])   #recoger los datos del usuario #getme("123") para token erroneo
    if meInformation == -1:
        return render_template('error.html')
    else:
        global meInfo #guardo la informacion del usuario para poder usarla en otros metodos y no tener que hacer más peticiones rest (tiempo ejecucion)
        meInfo = meInformation #guardar los datos en global para utilizarlos en otras paginas
        return render_template('myinfo.html',expiration=tokenInfo[1],name=meInfo['name'],email=meInfo['email'],photourl=meInfo['photourl']) #paso de los parámetros al html


@app.route('/createMessage',methods = ['POST', 'GET'])
def createMessage():
    if request.method == 'POST': #solo recoger los valores del formulario si entra por un post sino daría error 
        message = request.form['mensaje'] # mensaje para publicar en LID sacado del formulario
        responsePostMensage = postMessage(tokenInfo[0],message)
        if responsePostMensage == -1:
            return render_template('error.html')
        else:
            messageToHTML ="Tu mensaje se ha publicado: " + message + ' con ID: ' + responsePostMensage.json()['id'] #mensaje para publicar en el render, no es el que se ha posteado
            return render_template('myinfo.html',mensaje=messageToHTML,expiration=tokenInfo[1],name=meInfo['name'],email=meInfo['email'],photourl=meInfo['photourl'])
    else:
        return redirect('/myinfo')
### Funciones core

def gettoken(code):
    responsePostToken = post_authToken(code)
    if responsePostToken == -1:
        return -1
    else: 
        tokenInfo = [responsePostToken.json()['access_token'],responsePostToken.json()['expires_in']]
        return tokenInfo

def getmeemail (token):
    ResponseGetEmail = get_meEmail(token)
    if ResponseGetEmail == -1:
        return -1
    else:
        return ResponseGetEmail.json()['elements'][0]['handle~']['emailAddress']

def getme(token):
    
    ResponseGetMe = get_meInfo(token)
    ResponseGetEmail = getmeemail(token)
    if ResponseGetMe == -1 or ResponseGetEmail == -1:
        return -1
    else:
        name = ResponseGetMe.json()['firstName']['localized']['es_ES'] + " " + ResponseGetMe.json()['lastName']['localized']['es_ES']
        photoUrl = ResponseGetMe.json()['profilePicture']['displayImage~']['elements'][0]['identifiers'][0]['identifier']
        id = ResponseGetMe.json()['id']
        meInfo = {'email':ResponseGetEmail,'name':name,'photourl':photoUrl,'id':id}
        return meInfo

def postMessage(token,message):
    current_dateTime = datetime.now()
    messageToPost=message + ": " + str(current_dateTime)
    id = meInfo['id']
    ResponsePostMessage = post_message(token,messageToPost,id)
    if ResponsePostMessage == -1:
        return -1
    else:
        return ResponsePostMessage
### Funciones REST

def post_authToken (code):
    stringData='grant_type=authorization_code&code='+code+'&client_id='+clientId+'&client_secret='+clientSecret+'&redirect_uri='+urlRedirect+''
    Header =  {'Content-Type':'application/x-www-form-urlencoded','grant_type':'authorization_code'}
    response = requests.post('https://www.linkedin.com/oauth/v2/accessToken',data=stringData,headers=Header)
    print (response.status_code)
    if response.status_code != 200:
        return -1
    else:
        return response

def get_meInfo (token):
    Header={"Authorization": "Bearer " + token}
    response = requests.get(urlGetMe,headers=Header)
    print (response.status_code)
    if response.status_code != 200:
        print(response.json())
        return -1
    else:
        return response


def get_meEmail (token):
    Header={"Authorization": "Bearer " + token}
    response = requests.get(urlGetMeEmail,headers=Header)
    print (response.status_code)
    if response.status_code != 200:
        print(response.json())
        return -1
    else:
        return response

def post_message(token,message,id):
    Header={"Authorization": "Bearer " + token}
    userUrn = 'urn:li:person:'+id
    dataMessage = {
        'author': userUrn,
        'lifecycleState': 'PUBLISHED',
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": message
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
}
    response=requests.post(urlPostMessage,json=dataMessage,headers=Header)
    print (response.status_code)   
    if response.status_code != 201:
        print (response.json())
        return -1
    else:
        return response

### main 
if __name__ == '__main__':
    app.run()

