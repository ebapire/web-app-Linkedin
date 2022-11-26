import json
from datetime import datetime
import requests
clientId = '77sy8gqvao7mqx'
clientSecret = 'YtIPJyCc1CZnwOIz'
urlRedirect =  'http://eba77.com:5000/callback'
urlAuthToken = 'https://www.linkedin.com/oauth/v2/accessToken'
code = 'AQRBfeHjPTRUzS8tb4ic51Vp5SqXLnf9jXpOPaPA0-m49Pp5ybzVcxvQef7E_K-JREg4AjbF1QpvohjSkP0RSVBif-Vip89JJn-GG4H7f9iJA7VuLafvwFevgdWrNXY3SrL4n1jEJEolft_KnJ_waFThkQyyolJvm2MQqkFGYqA8XA6BZiUWuGXb7boD7HvAeno8kuSko9gfOBUserI'
urlGetMe = 'https://api.linkedin.com/v2/me'
urlGetMeEmail = 'https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))'

""" def gettoken(code):
    string='grant_type=authorization_code&code='+code+'&client_id='+clientId+'&client_secret='+clientSecret+'&redirect_uri='+urlRedirect+''
    token_request_body = {'code':code,'client_id':clientId,'client_secret':clientSecret,'redirect_uri':urlRedirect}
    token_request_body_str = json.dumps(token_request_body)
    Header =  {'Content-Type':'application/x-www-form-urlencoded','grant_type':'authorization_code'}
    response = requests.post('https://www.linkedin.com/oauth/v2/accessToken', data=string,headers=Header)
    return response.json()['access_token']

response = gettoken(code)
print(response.status_code)
print(response.json())
print(response.json()['accesstoken'])"""

authToken="AQX32uYQDjay9RnM7aFggsWPcnIqLisFzeE11C3CW8BmzK99DbmZVhOX6In7YW7K2hisoOITimGKtsD-zkRurGUiP4WZlWQ4COgZyoOO3bHaKL2kk0YB6nE-NrYgGxJjRZmBvtfxd2UlJTGHE_m0eqq-8tFlpNDFOCBrhalrgR5QLml1WuM8ZY0vfM0AAPrjdIUtdB4uWHwS6eoa8ABDpuHk7euv4dZhJ_BSic8fe_7XEFJqE-nm_LXHgNK_VSY_oy9q_Ma3FEaVvrTlCyMRDFfiDFrkKkoOhHYqANp9s7JzAuQVypHWW5MuXM9v16w_lTj51KQ-MIQnZZqSmSENWsc4jtgx5g"
params = {
  "client_id": clientId,
  "client_secret": clientSecret
}
Header={"Authorization": "Bearer " + authToken}
response = requests.get(urlGetMeEmail,headers=Header)

#print(response.json()['elements'][0]['handle~']['emailAddress'])


#ResponseGetMe.json()['firstName']['localized']['es_ES']
#json()['profilePicture']['displayImage~']['elements'][0]['identifiers'][0]['identifier']
#responseMethod = request.method
current_dateTime = datetime.now()
message='Hello World! This is my first Share on LinkedIn using the API REST!: ' + current_dateTime
response = requests.get(urlGetMe,headers=Header)

userUrn = 'urn:li:person:'+response.json()['id']
data_message = {
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
url = 'https://api.linkedin.com/v2/ugcPosts'
response=requests.post(url,json=data_message,headers=Header)