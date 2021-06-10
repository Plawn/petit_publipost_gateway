from .func_replacer import FuncReplacer


if __name__ == '__main__':
    def test(test_string: str):
        res = FuncReplacer.from_doc(test_string)[0]
        print(res)

        verify = FuncReplacer.to_doc(res)
        print(verify)
        print(verify == test_string)

    test_strings = [
        'mission.getStudentDoc___student_REM__',
        'mission.getStudentDoc__REM__'
    ]
    for test_string in test_strings:
        test(test_string)
