import os
import re

import docx2txt
import pandas

universities = (
    "2021.05.14. УФУ",
    "2021.05.14. ВГТУ",
    "2021.05.14. ВШЭ",
    "2021.05.14. МФТИ",
    "2021.05.14. НИЯУ МИФИ",
    "2021.05.14. ННГУ",
    "2021.05.14. СибГУ",
    "2021.05.14. СПБГУ",
    "2021.05.14. ТПУ",
    "2021.05.14. УжФУ",
    "2021.05.14. Финуниверситет",
    "2021.05.14. ЮУрГУ",
    "2021.05.17. НГУ",
    "2021.05.17. Самарский университет"
)

taxes = (
    "ML (AI)",
    "AR",
    "Аналитик данных",
    "Распределённые системы",
    "Геймдизайнер",
    "Образовательный дата-инженер"
)


def get_value(document_name, words):
    #print("Document: " + document_name)

    text = docx2txt.process(document_name).lower()

    s = 0
    for word in words:
        for lemma in re.sub(r"[^\w\s]", "", word).split():

            if len(lemma) < 3:
                continue

            count = text.count(lemma.lower())
            value = count * words[word]
            #print("Word: " + lemma.lower() + ", count: " + str(count) + ", value:", value)
            s += value

    return s


if __name__ == '__main__':
    print("Выберите ВУЗ:\n")
    for i in range(len(universities)):
        print(str(i) + " - " + universities[i])

    u = int(input())

    print("Выберите таксономию:\n")
    for i in range(len(taxes)):
        print(str(i) + " - " + taxes[i])

    t = int(input())

    if taxes[t] in ("AR", "Аналитик данных", "Распределённые системы", "Геймдизайнер", "Образовательный дата-инженер"):
        table = pandas.read_excel("./Таксономии на основе анализа рынка труда.xlsx", sheet_name=taxes[t])
        table = pandas.DataFrame(table)

        keys, values = tuple(table["TaxLevelName2"]), tuple(table["%"])

        words = dict()
        for i in range(5):
            words.setdefault(keys[i], values[i])
    else:
        table = pandas.read_excel("./Таксономии на основе анализа рынка труда.xlsx", sheet_name="ML (AI)")
        table = pandas.DataFrame(table)

        keys, values = tuple(table["Уровень таксономии2"]), tuple(table["%"])

        words = dict()
        for i in range(5):
            words.setdefault(keys[i], values[i])

    sum_university, sum_program, count_university, count_program = 0, 0, 0, 0
    programs = dict()

    for root, dirs, files in os.walk(".", topdown=False):
        for name in files:
            filepath = os.path.abspath(os.path.join(root, name))
            program = os.path.basename(os.path.dirname(filepath))
            university = filepath.replace("D:\\Projects\\PycharmProjects\\AIHack\\", "").split("\\")[0]

            if filepath.find(".docx") == -1 or filepath.find("~$") != -1 or filepath.find("venv") != -1:
                continue

            if university != universities[u]:
                continue

            value = get_value(filepath, words)

            print(value)

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

            print(university + ": " + str(sum_university) + ", " + str(count_university) + ", " + str(
                sum_university / count_university))

            sorted_programs = sorted(programs.items(), key=lambda item: item[1], reverse=True)
            programs = {k: v for k, v in sorted_programs}

    print(programs)
