import typing
try:
    from webcolors import name_to_rgb
except Exception as e:
    print(e)

class Parse:
    def __init__(self, file_name,):
        self.file_name = file_name
        self.line_count = 0
        self.key_count = 0
        self.nb_drones = 0
        self.lst = []
        self.lst2 = []
        self.start = ""
        self.end = ""
        self.zone_name = {}
        self.meta_dic = {}
        self.connections = []
        self.meta_connection_dic = {}

    def file_cleaner(self) -> int:
        try:
            with open(self.file_name,'r') as f:
                for ligne in f:
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
        nflag = 0
        space = 0
        try:
            for i in self.lst:
                self.line_count += 1
                if i == '':
                    space += 1
                    if space == len(self.lst):
                        raise ValueError(f"the file is empty")
                    continue
                if len(str(i).split(":", 1)) < 2:
                    raise ValueError(f"you should write a 'key: values' form")
                key, value = str(i).split(":", 1)
                key = key.strip()
                value = value.strip()
                if key.strip() not in ["nb_drones", "start_hub", "hub", "end_hub", "connection"]:
                    raise ValueError("the key you tipped is not correct.")
                if self.key_count == 0 and key != "nb_drones":
                    raise ValueError("the number drones must be first")
                if key == "nb_drones":
                    if nflag > 0:
                        raise ValueError("the key nb_drones is duplicate.")
                    try:
                        int_value = int(value)
                    except ValueError:
                        raise ValueError(f"'{value}' is not an integer.")
                    else:
                        if int_value <= 0:
                            raise ValueError(f"the 'nb_drones' must be positive integer {int_value} is not positive")
                        self.nb_drones = int_value
                        nflag += 1
                if key == 'start_hub':
                    if nflag == 0:
                        raise ValueError("you should add the 'nb_drones'.")
                    if sflag > 0:
                        raise ValueError("the key start_hub is duplicate.")
                    self.start_hub(value)
                    sflag += 1
                if key == 'end_hub':
                    if eflag > 0:
                        raise ValueError("the key end_hub is duplicate.")
                    if nflag == 0:
                        raise ValueError("you should add the 'nb_drones'.")
                    if sflag == 0:
                        raise ValueError("You need to add 'start_hub' before end_hub.")
                    self.end_hub(value)
                    eflag += 1
                if key == 'hub':
                    if eflag > 0:
                        raise ValueError("You can't add a hub after the 'end_hub'.")
                    if nflag == 0:
                        raise ValueError("you should add the 'nb_drones'.")
                    if sflag == 0:
                        raise ValueError("You need to add 'start_hub' before hub.")
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
                    if nflag == 0:
                        raise ValueError("you should add the 'nb_drones'.")
                    if sflag == 0:
                        raise ValueError("You need to add 'start_hub' before connection.")
                    if eflag == 0:
                        raise ValueError("You need to add 'end_hub' before connection.")
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
        except Exception as e:
            print(f"Error in line {self.line_count}: {e}")
            return None, None, None, None
        else:
            return self.nb_drones, self.zone_name, self.meta_dic, self.connections, self.meta_connection_dic, self.end, self.start


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
                raise ValueError("The name of zone is must change it already taken")
            if (x, y) in self.zone_name.values():
                raise ValueError("The values of coord 'hub' must change it already taken")
            self.zone_name[name.strip()] = (x, y)


    def start_hub(self, value: typing.Any):
        try:
            value = str(value).strip()
            if len(value.split()) > 3:
                l = value.split()
                int(l[1])
        except ValueError:
            raise ValueError("the name of the zone should not have a space in it.")
        if len(value.split()) == 3:
            try:
                name, x, y = value.split()
            except ValueError:
                raise ValueError("The 'start_hub' must just have : name x y [metadata].")
            else:
                if '-' in name:
                    raise ValueError("The '-' symbole can't be use in a name.")
                self.start = name
        elif len(value.split()) > 3:
            try:
                name, x, y, metadata = value.split(None,3)
            except ValueError:
                raise ValueError("The 'start_hub' must just have : name x y [metadata].")
            else:
                if '-' in name:
                    raise ValueError("The '-' symbole can't be use in a name.")
                self.meta_data_hubs(metadata,name.strip())
                self.start = name
        else:
            raise ValueError("The 'end_hub' must just have : name x y [metadata].")
        try:
            x = int(x)
            y = int(y)
        except ValueError:
            raise ValueError(f"check 'start_hub: name (integer) (integer).")
        else:
            self.zone_name[name.strip()] = (x, y)


    def end_hub(self, value: typing.Any):
        try:
            value = str(value).strip()
            if len(value.split()) > 3:
                l = value.split()
                int(l[1])
        except ValueError:
            raise ValueError("the name of the zone should not have a space in it")
        if len(value.split()) == 3:
            try:
                name, x, y = value.split()
            except ValueError:
                raise ValueError("The 'end_hub' must just have : name x y [metadata].")
            else:
                if '-' in name:
                    raise ValueError("The '-' symbole can't be use in a name")
                self.end = name
        elif len(value.split()) > 3:
            try:
                name, x, y, metadata = value.split(None, 3)
            except ValueError:
                raise ValueError("The 'end_hub' must just have : name x y [metadata].")
            else:
                if '-' in name:
                    raise ValueError("The '-' symbole can't be use in a name")
                self.end = name
                self.meta_data_hubs(metadata, name.strip())
        else:
            raise ValueError("The 'end_hub' must just have : name x y [metadata].")
        try:
            x = int(x)
            y = int(y)
        except ValueError:
            raise ValueError(f"check 'start_hub: name (positive integer) (positive integer)")
        else:
            if name.strip() in self.zone_name.keys():
                raise ValueError("The name of 'end_hub' must change it already taken")
            if (x, y) in self.zone_name.values():
                raise ValueError("The values of 'end_hub' must change it already taken")
            self.zone_name[name.strip()] = (x, y)


    def meta_data_hubs(self, metadata: str, key : str):
        z = 0
        c = 0
        d = 0
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
            if name == 'zone':
                if z >= 1:
                    raise ValueError("the key 'zone' is duplicate")
                z += 1
                if value.strip() not in ["normal","restricted","priority","blocked"]:
                    raise ValueError(f"The zone you written {value} is not a valid type the valid types are :['normal','restricted','priority','blocked']")
            if name == 'color':
                if c >= 1:
                    raise ValueError("the key 'color' is duplicate")
                c += 1
                try:
                    if value.strip().lower() == 'rainbow':
                        value = 'red'
                    name_to_rgb(value.strip().lower())
                except ValueError as error:
                    raise ValueError(error)
            if name == 'max_drones':
                if d >= 1:
                    raise ValueError("the key 'max_drones' is duplicate")
                d += 1
                try:
                    value = int(value)
                except ValueError:
                    raise ValueError(f"The value of 'max_drones' should be an integer")
                else:
                    if value < 0:
                        raise ValueError(f"The number of 'max_drones' should be positive")
            meta_keys.append(name)
            meta[name] = value
        self.meta_dic[key.strip()] = meta


    def connection(self, value: str) -> None:
        value = value.strip()
        self.check_dash(value)
        if  2 > len(value.split('-')) >= 3:
            raise ValueError(f"The connections must be between two zone names : zone1-zone2 .")
        x1, y1 = value.split('-')
        x1, y1 = x1.strip(), y1.strip()
        if x1 == y1 :
            raise ValueError(f"{x1} can't make a connexion with itself.")
        self.check_zone_name(x1)
        self.check_zone_name(y1)
        if self.connections:
            for connection in self.connections:
                self.check_dash(connection)
                x, y = connection.split('-')
                x, y = x.strip(), y.strip()
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
        else:
            if value < 0:
                raise ValueError(f"The number of 'max_link_capacity' should be positive")
        self.meta_connection_dic[self.connections[-1]] = value


    def check_dash(self, value: str):
        if value.count('-') > 1:
            raise ValueError(f"The connection should not have multiple dash between zones")
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
            raise ValueError(f"The name you've been given '{name}' has not been in any 'hub'.")


    def  check_equal(self,title: str) -> None:
        if '=' not in title:
            raise ValueError(f"The word you wrote have no '=' to indicate of 'key=value' pair." )

    
if __name__ == "__main__":
    x = Parse("config.txt")
    if 1 == x.file_cleaner():
        exit(1)
    try:
        nb, zones, metadic, connections, meta_connection_dic, end, start = x.parse_arguments()
    except Exception as e:
        print(e)
        exit(1)
    else:
        if zones is None or meta_connection_dic is None or connections is None or meta_connection_dic is None:
            exit(1)
        