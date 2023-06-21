import re

def correct_titles(string):
    abc = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    result = string.replace("-", " ")
    if result[0] in abc:
        result = result[0].upper() + result[1:]
    coincidencia = re.search("(.*)\s(\d{4})", string=result)
    if coincidencia:
        year = coincidencia.group(2)
        add = re.sub(".*\s(\d{4})", f" ({year})", result)
        result = coincidencia.group(1) + add
    return result

print(correct_titles("argentina-1985"))