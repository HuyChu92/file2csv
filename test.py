import pandas as pd
import tabula
from datetime import datetime
from tabula import read_pdf
from tabulate import tabulate

df = tabula.read_pdf(r'C:\Users\huy_c\source\repos\file2csv\test.pdf', pages="all")
output = pd.concat(df)


output.reset_index(inplace=True)
lijst_indexes = output.index.tolist()
print(lijst_indexes)
# print(output.head())