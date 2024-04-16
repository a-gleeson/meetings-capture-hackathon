import os

import pandas as pd


class Transcript:

    def __init__(self, file_path: str):
        self.file_path = file_path

        data = pd.read_csv(file_path)
        data.columns = [col.title() for col in data.columns]

        if not "Speaker" in data.columns:
            raise ValueError('No "Speaker" column in transcript')
        if not "Text" in data.columns:
            raise ValueError('No "Text" field found in transcript')

        if "Time" in data.columns:
            data = data.sort_values("Time")

        data["Approved?"] = False
        self.data = data

    def __repr__(self):
        return f"Transcript object stored at {self.file_path}\n\n{self.data.__repr__()}"

    def __str__(self):
        s = ""
        for ix, row in self.data.iterrows():
            s = f"{s}\n\n{row['Speaker']}: {row['Text']}"
        return s

    def __getitem__(self, key):
        return getattr(self.data, key)
