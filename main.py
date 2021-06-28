import os
import re

import docx2txt
import pandas

'''WORDS = list()

table = pandas.read_excel("./Таксономии на основе анализа рынка труда.xlsx", sheet_name="ML (AI)")
table = pandas.DataFrame(table)

keys, values = tuple(table["Уровень таксономии2"]), tuple(table["%"])

words = dict()
for i in range(5):
    words.setdefault(keys[i], values[i])
WORDS.append(words)'''

# for sheet in ("AR", "Аналитик данных", "Распределённые системы", "Геймдизайнер", "Образовательный дата-инженер"):
#     table = pandas.read_excel("./Таксономии на основе анализа рынка труда.xlsx", sheet_name=sheet)
#     table = pandas.DataFrame(table)
#
#     keys, values = tuple(table["TaxLevelName2"]), tuple(table["%"])
#
#     words = dict()
#     for i in range(5):
#         words.setdefault(keys[i], values[i])
#     WORDS.append(words)


def get_value(document_name, words):
    #print("Document: " + document_name)

    text = docx2txt.process(document_name).lower()

    s = 0
    for word in words:
        c = False
        for lemma in re.sub(r"[^\w\s]", "", word).split():

            if len(lemma) < 3:
                continue

            count = text.count(lemma.lower())
            #print("Word: " + lemma.lower() + ", count: " + str(count))
            if count > 2:
                c = True
        if c:
            s += 20

    return s


'''for words in WORDS:
    sum_university, sum_program, count_university, count_program = 0, 0, 0, 0
    universities, programs = dict(), dict()

    for root, dirs, files in os.walk(".", topdown=False):
        for name in files:
            filepath = os.path.abspath(os.path.join(root, name))
            program = os.path.basename(os.path.dirname(filepath))
            university = filepath.replace("D:\\Projects\\PycharmProjects\\AIHack\\", "").split("\\")[0]

            if filepath.find(".docx") == -1 or filepath.find("~$") != -1 or filepath.find("venv") != -1:
                continue

            value = get_value(filepath, words)

            print(value)

            if university not in universities:
                sum_university, count_university = 0, 0
                programs = dict()
                universities.setdefault(university, programs)

            sum_program += value
            count_program += 1

            if program not in programs.keys():
                sum_program, count_program = value, 1
                programs.setdefault(program, sum_program / count_program)
            else:
                programs[program] = sum_program / count_program

            sum_university += value
            count_university += 1

            if "Среднее значение по ОП" not in programs:
                programs.setdefault("Среднее значение по ОП", sum_university / count_university)
            else:
                programs["Среднее значение по ОП"] = (sum_university / count_university)

            print(university + ": " + str(sum_university) + ", " + str(count_university) + ", " + str(sum_university / count_university))

            sorted_programs = sorted(programs.items(), key=lambda item: item[1], reverse=True)
            universities[university] = {k: v for k, v in sorted_programs}

    sorted_universities = sorted(universities.items(), key=lambda item: list(item[1].items())[0][1], reverse=True)
    universities = {k: v for k, v in sorted_universities}

    print(universities, "\n")'''
