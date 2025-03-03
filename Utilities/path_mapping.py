import csv


class PathMapping(dict):

    csv_headers = ["Original Path", "New Path"]

    def __init__(self, *args):
        super().__init__(*args)

    def get_original_path(self, current_path):
        return next(key for key, value in self.items() if value == current_path)

    def remove_path(self, current_path):
        key = self.get_original_path(current_path)
        if key is None:
            raise Exception(f"Could not remove path mapping for {current_path}.")
        self.pop(key)

    def add_path(self, original_path, current_path):
        self.update({original_path: current_path})

    def update_path(self, current_path, new_path):
        key = next(key for key, value in self.items() if value == current_path)
        if key is None:
            raise Exception(f"Could not find path mapping for {current_path}.")
        self.update({key: new_path})

    def save(self, file_path):
        with open(file_path, "w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(self.csv_headers)
            for k, v in self.items():
                writer.writerow([k, v])

    @staticmethod
    def load(file_path):
        with open(file_path, "r") as csv_file:
            reader = csv.DictReader(csv_file)
            mapping_dict = {row[PathMapping.csv_headers[0]]: row[PathMapping.csv_headers[1]] for row in reader}
            return PathMapping(mapping_dict)
