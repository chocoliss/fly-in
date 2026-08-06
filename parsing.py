import typing


class Parse:
    def __init__(self, file_name,):
        self.file_name = file_name
        self.line_count = 0
        self.key_count = 0
        self.keys = []
        self.values = []
        self.lst = []
        self.lst2 = []

    def file_cleaner(self) -> int:
        if self.file_name != "config.txt":
            print("Error: The name of the file should be 'config.txt")
            return 1
        try:
            with open(self.file_name,'r') as f:
                for ligne in f:
                    if ligne[0] == '#':
                        continue
                    self.lst2.append(ligne.strip())
                for word in self.lst2:
                    i = 0
                    for c in word:
                        if c == '#':
                            word = word[:i]
                        i += 1
                    self.lst.append(word)
        except PermissionError as e:
            print("The config.txt has no permission")
            return 1
        else:
            return 0

    def parse_arguments(self) -> int:
        dic = {}
        try:
            for i in self.lst:
                self.line_count += 1
                if i == '':
                    continue
                key, value = i.split(':')
                if self.key_count == 0 and key != "nb_drones":
                    raise ValueError("the number drones must be first")
                if key.strip() not in ["nb_drones", "start_hub", "hub", "end_hub", "connection"]:
                    print(key)
                    raise ValueError("the key you tipped is not correct.")
                if self.keys.count("nb_dornes") > 1:
                    raise ValueError("the key nb_drones is duplicate")
                if self.keys.count("start_hub") > 1 :
                    raise ValueError("the key start_hub is duplicate")
                if self.keys.count("end_hub") > 1 :
                    raise ValueError("the key end_hub is duplicate")
                if key == "nb_drones":
                    try:
                        int_value = int(value)
                    except ValueError:
                        raise ValueError(f"{value} is not an integer")
                    else:
                        if int_value <= 0:
                            raise ValueError(f"the 'nb_drones' must be positive integer {int_value} is not positive")
                # if key == 'start_hub':
                #     self.start_hub()
                self.key_count += 1
                self.keys.append(key)
                self.values.append(value)
        except Exception as e:
            print(f"Error in line {self.line_count}: {e}")
            return 1
        else:
            print("done")
            return 0

    def start_hub(self):
        ...

if __name__ == "__main__":
    x = Parse("config.txt")
    if 1 == x.file_cleaner():
        exit(1)
    if x.parse_arguments() == 1:
        exit(1)
