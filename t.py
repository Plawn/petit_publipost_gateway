from dataclasses import dataclass


@dataclass
class test:
    a:str
    b:str


t = {
    'b':2,
    'a':'1',
}


p = test(**t)

print(p)

t = 'mission.documentReference__DDE__'