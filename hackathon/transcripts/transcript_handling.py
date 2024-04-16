import os

import pandas as pd


class Transcript:

    def __init__(self, file_path: str = None, data: pd.DataFrame = None):
        self.file_path = file_path

        if file_path is not None:
            data = pd.read_csv(file_path)
        data.columns = [col.title() for col in data.columns]

        if not "Speaker" in data.columns:
            raise ValueError('No "Speaker" column in transcript')
        if not "Text" in data.columns:
            raise ValueError('No "Text" field found in transcript')

        if "Time" in data.columns:
            data = data.sort_values("Time")

        if "Approved?" not in data.columns:
            data["Approved?"] = False
        else:
            data["Approved?"] = data["Approved?"].astype(bool)

        if data["Approved?"].all():
            self.is_approved = True
        else:
            self.is_approved = False

        data = data[[col for col in data.columns if "Unnamed" not in col]]

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

    def update_data(self, data: pd.DataFrame) -> None:
        self.data = data

    def save_transcript(self, write_path: str) -> None:
        if write_path[-4:] != ".csv":
            raise ValueError("Must be saved to a .csv!")

        self.data.to_csv(write_path, index=False)
