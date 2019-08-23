from app.better_publiposting import DocxTemplate
import json

doc = DocxTemplate('DDE.docx', '::')
res = doc.to_json()

template = {
        "mission::projectManager_student_firstName": '1jeb',
        "mission::contact_firstName": '2jeb',
        "mission::company_name": '3jeb',
        "mission::contact_civility_value": 'j4eb',
        "mission::company_address": '5jeb',
        "mission::projectManager_student_lastName": 'jeb',
        "mission::contact_lastName": 'je8b',
        "mission::company_zipCode": 'je7b',
        "mission::documentReference_p_DDE": 'j6eb',
        "mission::projectManager_student_civility_value": 'je5b',
        "mission::company_city": 'je6b',
        "mission::contact_position": 'je5b',
        "mission::projectManager_student_mail": 'je4b',
    }

templated = doc.apply_template(template)
templated.save('res.docx')

with open('res.json', 'w') as f:
    json.dump(res, f, indent=4)


