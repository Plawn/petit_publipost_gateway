

raise DeprecationWarning("This test file is deprecated")

import json

from app.better_publiposting import DocxTemplate
from app.better_publiposting.ReplacerMiddleware import (FuncReplacer,
                                                        ListReplacer,
                                                        MultiReplacer)

m = MultiReplacer([FuncReplacer(), ListReplacer()])
doc = DocxTemplate('DDE.docx', m)

res = doc.to_json()
# mission.contact.civility.value
template = {
    'mission': {
        # 'contact': {
        #     'civility': {
        #         'value': 'JEB'
        #     },
        #     # 'firstName':'Paul'
        # },
        'projectManager': {
            'student': {
                'firstName': 'Paul',
                'lastName': 'Leveau'
            }
        },
        #     'documentReference("DDE")': 'DAT REF',
        #     # 'documentReference(\"DDE\")': "SOME ref",
        #     'nbJEH': 10,
        #     # need name and price for phases
        #     'phases': [
        #         {'name': 'Phase1', 'price': 5},
        #         {'name': 'Phase2', 'price': 3},
        #         {'name': 'Phase3', 'price': 2}
        #     ],
        #     'Frais': '200',
        #     'accomptePerc': '30'
        # },
        # 'student': {
        #     'name': {
        #         'value': 'Paul'
        #     }
        # }
    }
}


templated = doc.apply_template(template)
templated.save('res.docx')

with open('res.json', 'w') as f:
    json.dump(res, f, indent=4)
