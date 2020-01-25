from typing import Dict
import json


def from_strings_to_dict(data: Dict[str, str]):
    """
    Makes a model for a given list of string like :

    "mission.document.name": "test" => {
        mission: {
            document: {
                name: "test"
            }
        }
    }
    This way we will merge the model with the input in order to ensure that placeholder are replaced with what we want
    """
    res = {}
    for key, value in data.items():
        l = key.split('.')
        previous = []
        end = len(l) - 1
        for i, item in enumerate(l):
            d = res
            last_node = None
            last_prev = None
            for prev in previous[:-1]:
                d = d[prev]
                last_node = d
                last_prev = prev

            if len(previous) > 0:
                d = d[previous[-1]]
                last_prev = previous[-1]

            if item not in d:
                if i != end:
                    d[item] = {}
                else:
                    d[item] = value
            previous.append(item)
    return res


data = {
    "mission.contact.civility.value": "M.",
    "mission.company.name": "Naturalia",
    "mission.contact.position": "Directeur RH",
    "mission.projectManager.student.civility.value":
    "M.", "mission.company.zipCode": "",
    "mission.projectManager.student.lastName": "LEVEAU",
    "mission.company.city": "Paris",
    "mission.projectManager.student.mail": "paul.leveau@gmail.com",
    "mission.projectManager.student.firstName": "Paul",
    "mission.contact.firstName": "Baptiste", "mission.company.address": "",
    "mission.contact.lastName": "Léon", "mission.documentReference(\"DDE\")": "DDE-2093-11241-01-2020-01"
}

print(json.dumps(from_strings_to_dict(data), indent=4))