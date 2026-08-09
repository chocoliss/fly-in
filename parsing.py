import typing
from webcolors import name_to_rgb


class Parse:
    def __init__(self, file_name,):
        self.file_name = file_name
        self.line_count = 0
        self.key_count = 0
        self.keys = []
        self.values = []
        self.lst = []
        self.lst2 = []
        self.zone_name = {}
        self.meta_dic = {}
        self.connections = []
        self.meta_connection_dic = {}

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
        sflag = 0
        eflag = 0
        try:
            for i in self.lst:
                self.line_count += 1
                if i == '':
                    continue
                if len(str(i).split(":", 1)) < 2:
                    raise ValueError(f"you should write a 'key: values' form")
                key, value = str(i).split(":", 1)
                key = key.strip()
                value = value.strip()
                if self.key_count == 0 and key != "nb_drones":
                    raise ValueError("the number drones must be first")
                if key.strip() not in ["nb_drones", "start_hub", "hub", "end_hub", "connection"]:
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
                        raise ValueError(f"'{value}' is not an integer")
                    else:
                        if int_value <= 0:
                            raise ValueError(f"the 'nb_drones' must be positive integer {int_value} is not positive")
                if key == 'start_hub':
                    self.start_hub(value)
                if key == 'end_hub':
                    self.end_hub(value)
                if key == 'hub':
                    if len(value.split()) < 3:
                        raise ValueError(f"you missed a value the line should be : hub: name x y")
                    if len(value.split()) > 3:
                        try :
                            name, x, y, metadata = value.split(None, 3)
                        except ValueError:
                            raise ValueError("The hub must have: name x y [(optinnal) zone=... color=... max_drones=... ]")
                        else:
                            self.meta_data_hubs(metadata,name)
                    if len(value.split()) == 3:
                            name, x, y = value.split()
                    self.hub(name, x, y)
                if key == 'connection':
                    if len(value.split(None, 1)) > 2:
                        raise ValueError(f"Wrote more than two arguments {value}.\nConnection: zone1-zone2 [metadata (optionnal)]")
                    elif len(value.split(None, 1)) == 2:
                        connection, metdata = value.split(None, 1)
                        self.connection(connection)
                        self.meta_data_connections(metdata)
                    elif len(value.split(None, 1)) == 1:
                        try:
                            connection = value.strip()
                        except ValueError:
                            raise ValueError(f"The connection is not a string {connection}")
                        self.connection(connection)
                self.key_count += 1
                self.keys.append(key)
                self.values.append(value)
        except Exception as e:
            print(f"Error in line {self.line_count}: {e}")
            return 1
        else:
            print(self.zone_name)
            print(self.meta_dic)
            print(self.meta_connection_dic)
            print(self.connections)
            print("done")
            return 0


    def hub(self, name: str, x: str, y: str):
        if '-' in name:
            raise ValueError("The '-' symbole can't be use in a name")
        try:
            x = int(x)
            y = int(y)
        except Exception:
            raise ValueError("The name of the zone can't have space in it")
        else:
            if name.strip() in self.zone_name:
                raise ValueError("The name of zone is repeated")
            self.zone_name[name.strip()] = (x, y)


    def start_hub(self, value: typing.Any):
        try:
            value = str(value).strip()
            if len(value.split()) > 3:
                l = value.split()
                int(l[1])
        except ValueError:
            raise ValueError("the name of the zone should not have a space in it")
        try:
            name, x, y = value.split()
        except ValueError:
            raise ValueError("The 'start_hub' must just have : name x y")
        else:
            if '-' in name:
                raise ValueError("The '-' symbole can't be use in a name")
            self.zone_name[name.strip()] = (x.strip(), y.strip())
            return

    def end_hub(self, value: typing.Any):
        try:
            value = str(value).strip()
            if len(value.split()) > 3:
                l = value.split()
                int(l[1])
        except ValueError:
            raise ValueError("the name of the zone should not have a space in it")
        try:
            name, x, y = value.split()
        except ValueError:
            raise ValueError("The 'end_hub' must just have : name x y")
        else:
            if '-' in name:
                raise ValueError("The '-' symbole can't be use in a name")
            if name in self.zone_name.keys():
                raise ValueError("The name of 'end_hub' must change")
            self.zone_name[name] = (x.strip(), y.strip())
            return

    def meta_data_hubs(self, metadata: str, key : str):
        meta = {}
        meta_keys = []
        x = metadata.strip()
        if x[0] != '[' and x[-1] != ']':
            raise ValueError(f"The metadata should be in '[key=value key=value ...]' not this {x}")
        self.check_brackets(x)
        x = x[1:-1].strip()
        if x.strip() == '':
            raise ValueError("The bracket of metadata should not be empty")
        if len(x.split()) > 3 :
            raise ValueError(f"You made a mistake in metadata keys as most three \nThe keys are: 'zone' 'color' 'max_drones'.")
        for title in x.split():
            self.check_equal(title)
            name ,value  = title.split('=')
            name = name.strip()
            if name not in ["zone", "color", "max_drones"]:
                raise ValueError(f"The key of the metadata you tipped {name} is not valid \nThe keys are: 'zone' 'color' 'max_drones'.")
            if meta_keys.count("zone") > 1:
                    raise ValueError("the key zone is duplicate")
            if meta_keys.count("color") > 1 :
                    raise ValueError("the key color is duplicate")
            if meta_keys.count("max_drones") > 1 :
                    raise ValueError("the key max_drones is duplicate")
            if name == 'zone':
                if value.strip() not in ["normal","restricted","priority","blocked"]:
                    raise ValueError(f"The zone you written {value} is not a valid type the valid types are :['normal','restricted','priority','blocked']")
            if name == 'color':
                try:
                    name_to_rgb(value.strip().lower())
                except ValueError as error:
                    raise ValueError(error)
            if name == 'max_drones':
                try:
                    value = int(value)
                except ValueError:
                    raise ValueError(f"The value of 'max_drones' should be an integer")
            meta_keys.append(name)
            meta[name] = value
        self.meta_dic[key.strip()] = meta


    def connection(self, value: str) -> None:
        print(value)
        value = value.strip()
        self.check_dash(value)
        if  2 > len(value.split('-')) >= 3:
            raise ValueError(f"The connections must be between two zone names : zone1-zone2 .")
        x1, y1 = value.split('-')
        x1, y1 = x1.strip(), y1.strip()
        self.check_zone_name(x1)
        self.check_zone_name(y1)
        if self.connections:
            for connection in self.connections:
                self.check_dash(connection)
                x, y = connection.split('-')
                x, y = x.strip(), y.strip()
                print(f"{x}, {x1} ,{y}, {y1}")
                if (x1 == x and y1 == y) or (x1 == y and y1 == x):
                    raise ValueError(f"The connection {connection} is the same as {value}.\nThe connections should not be repeated.")
        self.connections.append(value)


    def meta_data_connections(self, metdata: str) -> None:
        x = metdata.strip()
        if x[0] != '[' and x[-1] != ']':
            raise ValueError(f"The metadata should be in '[max_link_capacity=value]' not this {x}.")
        self.check_brackets(x)
        x = x[1:-1].strip()
        if x.strip() == '':
            raise ValueError("The bracket of metadata should not be empty")
        if len(x.split()) > 1 :
            raise ValueError(f"You made a mistake in metadata [max_link_capacity=value]in connection.")
        self.check_equal(x)
        name ,value  = x.split('=')
        name = name.strip()
        if name != 'max_link_capacity':
            raise ValueError(f"The key of the metadata you tipped {name} is not valid. \nShould be 'max_link_capacity'")
        try:
            value = int(value)
        except ValueError:
            raise ValueError(f"The value of 'max_link_capacity' should be an integer")
        self.meta_connection_dic[self.connections[-1]] = value


    def check_dash(self, value: str):
        if '-' not in value:
            raise ValueError(f"No dash between connections '{value}'")
        if '-' == value[0] or '-' == value[-1]:
            raise ValueError(f"Dash should be between zone names no space between them : {value}\nzone1-zone2")


    def check_brackets(self,sentance: str):
        i = 0
        for c in sentance[1:-1]:
            if c == ']':
               raise ValueError(f"The ] bracket should be one in the end you forgot this ']' in colone {i}")
            if c == '[':
                raise ValueError(f"you oppend the bracket two times in colone {i}")
            i += 1
        return


    def check_zone_name(self, name: str) -> None:
        if name not in self.zone_name.keys():
            raise ValueError(f"The name you've been given {name} has not been in any 'hub'.")


    def  check_equal(self,title: str) -> None:
        if '=' not in title:
            raise ValueError(f"The word you wrote have no '=' to indicate of 'key=value' pair." )

    
if __name__ == "__main__":
    x = Parse("config.txt")
    if 1 == x.file_cleaner():
        exit(1)
    if x.parse_arguments() == 1:
        exit(1)