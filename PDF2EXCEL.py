import pandas as pd
import tabula
from datetime import datetime
from tabula import read_pdf
from tabulate import tabulate

df = tabula.read_pdf(r'C:\Users\huy_c\source\repos\file2csv\test.pdf', pages="all")

resultaat = []

for frame in df:
    if frame.shape[1] == 4:
        f = frame.iloc[1:, :]
        resultaat.append(f)

output = pd.concat(resultaat)


stringTijd = output["Date"]
tijd = []
# Zet datetimestring om in datetime object
for t in stringTijd:
    date_time_obj = datetime.strptime(t, '%d.%m.%Y %H:%M:%S')
    tijd.append(date_time_obj)

cumulatieveTijd = []
cumulatieveTijd.append(tijd[0])
current = tijd[0]
nieuw = tijd[1] - tijd[0]
for t in tijd[1:]:
    verschil = t - current
    cumulatieveTijd.append(verschil)
    nieuw += verschil

output['Verschil'] = cumulatieveTijd
print(output.dtypes)

#output.to_csv('output.csv')
output.to_excel('excel.xlsx')

verschilDagen = tijd[-1] - tijd[0]
# print(verschilDagen)








