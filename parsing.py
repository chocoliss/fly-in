"""Parse and validate Fly-in map files."""

from __future__ import annotations

from typing import Any, TypeAlias


Coordinates: TypeAlias = tuple[int, int]
MetadataValue: TypeAlias = str | int
ZoneMetadata: TypeAlias = dict[str, MetadataValue]
Zones: TypeAlias = dict[str, Coordinates]
Metadata: TypeAlias = dict[str, ZoneMetadata]
ParseSuccess: TypeAlias = tuple[
    int,
    Zones,
    Metadata,
    list[str],
    dict[str, int],
    str,
    str,
]


class Parse:
    """Read a map file and build the data used by the project."""

    def __init__(self, file_name: str) -> None:
        """Initialize an empty parser for ``file_name``."""
        self.file_name = file_name
        self.line_count = 0
        self.key_count = 0
        self.nb_drones = 0
        self.lst: list[str] = []
        self.lst2: list[str] = []
        self.start = ""
        self.end = ""
        self.zone_name: Zones = {}
        self.meta_dic: Metadata = {}
        self.connections: list[str] = []
        self.meta_connection_dic: dict[str, int] = {}

    def file_cleaner(self) -> int:
        """Read the map and remove comments from every input line."""
        try:
            with open(self.file_name, 'r') as f:
                for ligne in f:
                    self.lst2.append(ligne.strip())
                for word in self.lst2:
                    i = 0
                    for c in word:
                        if c == '#':
                            word = word[:i]
                        i += 1
                    self.lst.append(word)
        except PermissionError:
            print("The config.txt has no permission")
            return 1
        else:
            return 0

    def parse_arguments(self) -> ParseSuccess:
        """Parse all cleaned lines or raise a line-numbered error."""
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
                        raise ValueError("the file is empty")
                    continue
                if len(str(i).split(":", 1)) < 2:
                    raise ValueError("you should write a 'key: values' form")
                key, value = str(i).split(":", 1)
                key = key.strip()
                value = value.strip()
                if key.strip() not in [
                    "nb_drones",
                    "start_hub",
                    "hub",
                    "end_hub",
                        "connection"]:
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
                            raise ValueError(
                                "the 'nb_drones' must be positive integer "
                                f"{int_value} is not positive"
                            )
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
                        raise ValueError(
                            "You need to add 'start_hub' before end_hub.")
                    self.end_hub(value)
                    eflag += 1
                if key == 'hub':
                    if eflag > 0:
                        raise ValueError(
                            "You can't add a hub after the 'end_hub'.")
                    if nflag == 0:
                        raise ValueError("you should add the 'nb_drones'.")
                    if sflag == 0:
                        raise ValueError(
                            "You need to add 'start_hub' before hub.")
                    if len(value.split()) < 3:
                        raise ValueError(
                            "you missed a value the line should be : "
                            "hub: name x y"
                        )
                    if len(value.split()) > 3:
                        try:
                            name, x, y, metadata = value.split(None, 3)
                        except ValueError:
                            raise ValueError(
                                "The hub must have: name x y "
                                "[(optinnal) zone=... color=... "
                                "max_drones=... ]"
                            )
                        else:
                            self.meta_data_hubs(metadata, name)
                    if len(value.split()) == 3:
                        name, x, y = value.split()
                    self.hub(name, x, y)
                if key == 'connection':
                    if nflag == 0:
                        raise ValueError("you should add the 'nb_drones'.")
                    if sflag == 0:
                        raise ValueError(
                            "You need to add 'start_hub' before connection.")
                    if eflag == 0:
                        raise ValueError(
                            "You need to add 'end_hub' before connection.")
                    if len(value.split(None, 1)) > 2:
                        raise ValueError(
                            f"Wrote more than two arguments {value}.\n"
                            "Connection: zone1-zone2 "
                            "[metadata (optionnal)]"
                        )
                    elif len(value.split(None, 1)) == 2:
                        connection, metdata = value.split(None, 1)
                        self.connection(connection)
                        self.meta_data_connections(metdata)
                    elif len(value.split(None, 1)) == 1:
                        try:
                            connection = value.strip()
                        except ValueError:
                            raise ValueError(
                                "The connection is not a string "
                                f"{connection}"
                            )
                        self.connection(connection)
                self.key_count += 1
        except (IndexError, ValueError) as error:
            raise ValueError(
                f"Error in line {self.line_count}: {error}"
            ) from error
        else:
            return (
                self.nb_drones,
                self.zone_name,
                self.meta_dic,
                self.connections,
                self.meta_connection_dic,
                self.end,
                self.start,
            )

    def hub(self, name: str, x: str, y: str) -> None:
        """Validate and store one ordinary hub."""
        if '-' in name:
            raise ValueError("The '-' symbole can't be use in a name")
        try:
            x_value = int(x)
            y_value = int(y)
        except Exception:
            raise ValueError("The name of the zone can't have space in it")
        else:
            if name.strip() in self.zone_name:
                raise ValueError(
                    "The name of zone is must change it already taken")
            if (x_value, y_value) in self.zone_name.values():
                raise ValueError(
                    "The values of coord 'hub' must change it already taken")
            self.zone_name[name.strip()] = (x_value, y_value)

    def start_hub(self, value: Any) -> None:
        """Validate and store the start hub and its optional metadata."""
        try:
            value = str(value).strip()
            if len(value.split()) > 3:
                parts = value.split()
                int(parts[1])
        except ValueError:
            raise ValueError(
                "the name of the zone should not have a space in it.")
        if len(value.split()) == 3:
            try:
                name, x, y = value.split()
            except ValueError:
                raise ValueError(
                    "The 'start_hub' must just have : name x y [metadata].")
            else:
                if '-' in name:
                    raise ValueError(
                        "The '-' symbole can't be use in a name."
                    )
                self.start = name
        elif len(value.split()) > 3:
            try:
                name, x, y, metadata = value.split(None, 3)
            except ValueError:
                raise ValueError(
                    "The 'start_hub' must just have : name x y [metadata].")
            else:
                if '-' in name:
                    raise ValueError("The '-' symbole can't be use in a name.")
                self.meta_data_hubs(metadata, name.strip())
                self.start = name
        else:
            raise ValueError(
                "The 'end_hub' must just have : name x y [metadata].")
        try:
            x_value = int(x)
            y_value = int(y)
        except ValueError:
            raise ValueError("check 'start_hub: name (integer) (integer).")
        else:
            self.zone_name[name.strip()] = (x_value, y_value)

    def end_hub(self, value: Any) -> None:
        """Validate and store the end hub and its optional metadata."""
        try:
            value = str(value).strip()
            if len(value.split()) > 3:
                parts = value.split()
                int(parts[1])
        except ValueError:
            raise ValueError(
                "the name of the zone should not have a space in it")
        if len(value.split()) == 3:
            try:
                name, x, y = value.split()
            except ValueError:
                raise ValueError(
                    "The 'end_hub' must just have : name x y [metadata].")
            else:
                if '-' in name:
                    raise ValueError("The '-' symbole can't be use in a name")
                self.end = name
        elif len(value.split()) > 3:
            try:
                name, x, y, metadata = value.split(None, 3)
            except ValueError:
                raise ValueError(
                    "The 'end_hub' must just have : name x y [metadata].")
            else:
                if '-' in name:
                    raise ValueError("The '-' symbole can't be use in a name")
                self.end = name
                self.meta_data_hubs(metadata, name.strip())
        else:
            raise ValueError(
                "The 'end_hub' must just have : name x y [metadata].")
        try:
            x_value = int(x)
            y_value = int(y)
        except ValueError:
            raise ValueError(
                "check 'start_hub: name (positive integer) "
                "(positive integer)"
            )
        else:
            if name.strip() in self.zone_name.keys():
                raise ValueError(
                    "The name of 'end_hub' must change it already taken")
            if (x_value, y_value) in self.zone_name.values():
                raise ValueError(
                    "The values of 'end_hub' must change it already taken")
            self.zone_name[name.strip()] = (x_value, y_value)

    def meta_data_hubs(self, metadata: str, key: str) -> None:
        """Validate and store metadata belonging to one hub."""
        z = 0
        c = 0
        d = 0
        meta: ZoneMetadata = {}
        meta_keys: list[str] = []
        x = metadata.strip()
        if x[0] != '[' and x[-1] != ']':
            raise ValueError(
                "The metadata should be in "
                f"'[key=value key=value ...]' not this {x}"
            )
        self.check_brackets(x)
        x = x[1:-1].strip()
        if x.strip() == '':
            raise ValueError("The bracket of metadata should not be empty")
        if len(x.split()) > 3:
            raise ValueError(
                "You made a mistake in metadata keys as most three \n"
                "The keys are: 'zone' 'color' 'max_drones'."
            )
        for title in x.split():
            self.check_equal(title)
            name, raw_value = title.split('=')
            name = name.strip()
            value: MetadataValue = raw_value
            if name not in ["zone", "color", "max_drones"]:
                raise ValueError(
                    "The key of the metadata you tipped "
                    f"{name} is not valid \n"
                    "The keys are: 'zone' 'color' 'max_drones'."
                )
            if name == 'zone':
                if z >= 1:
                    raise ValueError("the key 'zone' is duplicate")
                z += 1
                if raw_value.strip() not in [
                    "normal",
                    "restricted",
                    "priority",
                    "blocked",
                ]:
                    raise ValueError(
                        "The zone you written "
                        f"{raw_value} is not a valid type the valid types "
                        "are :['normal','restricted','priority','blocked']"
                    )
            if name == 'color':
                if c >= 1:
                    raise ValueError("the key 'color' is duplicate")
                c += 1
                value = raw_value.strip()
            if name == 'max_drones':
                if d >= 1:
                    raise ValueError("the key 'max_drones' is duplicate")
                d += 1
                try:
                    value = int(raw_value)
                except ValueError:
                    raise ValueError(
                        "The value of 'max_drones' should be an integer"
                    )
                else:
                    if value <= 0:
                        raise ValueError(
                            "The number of 'max_drones' should be positive"
                        )
            meta_keys.append(name)
            meta[name] = value
        self.meta_dic[key.strip()] = meta

    def connection(self, value: str) -> None:
        """Validate and store one bidirectional connection."""
        value = value.strip()
        self.check_dash(value)
        if 2 > len(value.split('-')) >= 3:
            raise ValueError(
                "The connections must be between two zone names : "
                "zone1-zone2 ."
            )
        x1, y1 = value.split('-')
        x1, y1 = x1.strip(), y1.strip()
        if x1 == y1:
            raise ValueError(f"{x1} can't make a connexion with itself.")
        self.check_zone_name(x1)
        self.check_zone_name(y1)
        if self.connections:
            for connection in self.connections:
                self.check_dash(connection)
                x, y = connection.split('-')
                x, y = x.strip(), y.strip()
                if (x1 == x and y1 == y) or (x1 == y and y1 == x):
                    raise ValueError(
                        f"The connection {connection} is the same as "
                        f"{value}.\nThe connections should not be repeated."
                    )
        self.connections.append(value)

    def meta_data_connections(self, metdata: str) -> None:
        """Validate and store the capacity of the latest connection."""
        x = metdata.strip()
        if x[0] != '[' and x[-1] != ']':
            raise ValueError(
                "The metadata should be in "
                f"'[max_link_capacity=value]' not this {x}."
            )
        self.check_brackets(x)
        x = x[1:-1].strip()
        if x.strip() == '':
            raise ValueError("The bracket of metadata should not be empty")
        if len(x.split()) > 1:
            raise ValueError(
                "You made a mistake in metadata "
                "[max_link_capacity=value]in connection."
            )
        self.check_equal(x)
        name, raw_value = x.split('=')
        name = name.strip()
        if name != 'max_link_capacity':
            raise ValueError(
                "The key of the metadata you tipped "
                f"{name} is not valid. \n"
                "Should be 'max_link_capacity'"
            )
        try:
            value = int(raw_value)
        except ValueError:
            raise ValueError(
                "The value of 'max_link_capacity' should be an integer"
            )
        else:
            if value <= 0:
                raise ValueError(
                    "The number of 'max_link_capacity' should be positive"
                )
        self.meta_connection_dic[self.connections[-1]] = value

    def check_dash(self, value: str) -> None:
        """Check that a connection contains exactly one internal dash."""
        if value.count('-') > 1:
            raise ValueError(
                "The connection should not have multiple dash between zones"
            )
        if '-' not in value:
            raise ValueError(f"No dash between connections '{value}'")
        if '-' == value[0] or '-' == value[-1]:
            raise ValueError(
                "Dash should be between zone names no space between them : "
                f"{value}\nzone1-zone2"
            )

    def check_brackets(self, sentance: str) -> None:
        """Reject extra square brackets inside a metadata block."""
        i = 0
        for c in sentance[1:-1]:
            if c == ']':
                raise ValueError(
                    "The ] bracket should be one in the end you forgot "
                    f"this ']' in colone {i}"
                )
            if c == '[':
                raise ValueError(
                    f"you oppend the bracket two times in colone {i}"
                )
            i += 1
        return

    def check_zone_name(self, name: str) -> None:
        """Check that a connection endpoint names a known hub."""
        if name not in self.zone_name.keys():
            raise ValueError(
                "The name you've been given "
                f"'{name}' has not been in any 'hub'."
            )

    def check_equal(self, title: str) -> None:
        """Check that a metadata item uses the ``key=value`` form."""
        if '=' not in title:
            raise ValueError(
                "The word you wrote have no '=' to indicate of "
                "'key=value' pair."
            )
