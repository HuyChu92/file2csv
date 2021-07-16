import pandas as pd

class Dataframe:
    
    def __init__(self,df):
        self.df = df 

    def show_average(self):
        return self.kolom.mean()