import json
import pytablewriter
from scipy.special import binom

def calc_distribution(cards):
    distr = {}
    for card in cards:
        distr[card[1:2]] = distr.get(card[1:2], 0) + 1
    return distr

def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z

data = [
        "skatstube_236000000_to_236099999.json",
        "skatstube_236100000_to_236199999.json",
        "skatstube_236200000_to_236299999.json",
        "skatstube_236300000_to_236399999.json",
        "skatstube_236400000_to_236499999.json",
        "skatstube_236500000_to_236599999.json",
        "skatstube_236600000_to_236699999.json",
        "skatstube_236700000_to_236799999.json",
        "skatstube_236800000_to_236899999.json",
        ]

result = {}

for data_file in data:
    with open(data_file,"r") as handle:
        result.update(json.load(handle))

sums = {}
for key in result.keys():
    value = result[key]
    for hand in value[1:4]:
        distr = calc_distribution(hand)
        b = str(distr.get('U', 0))
        a = str(distr.get('A', 0))
        z = str(distr.get('X', 0))
        sums[b+a+z] = sums.get(b+a+z,0) + 1
        sums[b+'xx'] = sums.get(b+'xx',0) + 1
        sums['x'+a+'x'] = sums.get('x'+a+'x',0) + 1
        sums['xx'+z] = sums.get('xx'+z, 0) + 1
        sums[b+a+'x'] = sums.get(b+a+'x', 0) + 1
        sums[b+'x'+z] = sums.get(b+'x'+z, 0) + 1
        sums['x'+a+z] = sums.get('x'+a+z, 0) + 1


writer = pytablewriter.MarkdownTableWriter()
writer.table_name = "Auswertung Spiel 236000000 bis 236799999 (2.700.000 Haende)"
writer.header_list = ["Bube", "Ass", "Zehn", "Anzahl", "Ist", "Soll", "Abweichung(%)"]
writer.value_matrix = []

def calc_should_value(b,a,z):
    cnt = 0
    cnt2 = 0
    binoms = []
    for x in [b,a,z]:
        if x is not 'x':
            cnt += 1
            cnt2 += int(x)
            binoms.append(binom(4,int(x)))
    upper = binom(32-cnt*4, 10-cnt2)
    for pos in binoms:
        if pos is not None:
            upper = upper * pos
    return upper/binom(32,10)

total = 0

for key in sorted(sums.keys(), reverse=True):
    b,a,z = key[0],key[1],key[2]
    wert = sums.get(key)/float(len(result)*3)
    should = calc_should_value(b,a,z)
    writer.value_matrix.append([b,a,z,sums.get(key),wert,should,(100*(wert-should))/should])
    total += sums.get(key)*((100*(wert-should))/should)

total/= len(result)
print("x: beliebig viele / ")
print("Gewichtete Abweichung: "+str(total)+"%")
print("")
writer.write_table()
