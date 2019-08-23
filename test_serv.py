import requests
import json

url = 'http://localhost:5000'

data = {
    'data': json.dumps({
        'mission': {
            'projectManager_student_firstName': 'Heb'
        }}),
    'document_name': 'DDE',
    'filename': 'test.docx',
    'type': 'mission'
}

r = requests.post(url+'/publipost', data=data)
print(r, r.text)
