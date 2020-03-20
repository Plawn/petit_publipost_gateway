class test1:
    __t = None

    @classmethod
    def c(cls, p):
        cls.__t = p

    def __repr__(self):
        return f'{self.__t}'

class a(test1):
    pass

class b(test1):
    pass




a1 = a()
a1.c(2)

b1 = b()
b1.c(3)

print(a1)
print(b1)

