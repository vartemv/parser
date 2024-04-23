import sys
import re
import xml.etree.ElementTree as ET
order = 1

def check_validity(token, length):
        if len(token) != length:
            print(f"You have wrong amount of variables in {token[0]} call", file=sys.stderr)
            sys.exit(23)

def name_validity(first_character):
        allowed_characters = ["_", "-", "$", "&", "%", "*", "!", "?"]
        if not first_character.isalpha() and first_character not in allowed_characters:
            print("Forbidden name", file=sys.stderr)
            sys.exit(23)

def detect_type(token, types):
        for i in range(1, len(token)):
            tmp = token[i].split("@", 1)

            if types[i - 1] == "var" and tmp[0] not in ["GF", "LF", "TF"]:
                print(f"You must use only variables here: {token[0]}", file=sys.stderr)
                sys.exit(23)

            if types[i - 1] != "label" and len(tmp) != 2 and token[0] != "READ":
                print("You provided argument without type or frame declaration", file=sys.stderr)
                sys.exit(23)

            if len(tmp) == 2:
                if types[i - 1] == "label":
                    print("You have variable where it is forbidden", file=sys.stderr)
                    sys.exit(23)

                if tmp[0] in ["GF", "TF", "LF"]:
                    if types[i - 1] in ["var", "symb"]:
                        types[i - 1] = "var"
                    else:
                        print("You have variable declaration where it isn't expected", file=sys.stderr)
                        sys.exit(23)

                    name_validity(str(tmp[1][0]))

                elif tmp[0] in ["int", "string", "bool", "nil"] and types[i - 1] == "symb":
                    if tmp[0] == "string":
                        if isinstance(tmp[1], str):
                            tmp[1] = string_serialization(tmp[1])
                        else:
                            print(f"Wrong type usage {token[i]}", file=sys.stderr)
                            sys.exit(23)
                    elif tmp[0] == "int":
                        try:
                            int(tmp[1])
                        except ValueError:
                            try:
                                int(tmp[1], base=8)
                            except ValueError:
                                try:
                                    int(tmp[1], base=16)
                                except ValueError:
                                    print(f"You have wrong int type", file=sys.stderr)
                                    sys.exit(23)
                    elif tmp[0] == "bool":
                        if tmp[1] not in ["true", "false"]:
                            print(f"Problem with bool usage - {token[i]}", file=sys.stderr)
                            sys.exit(23)
                    elif tmp[0] == "nil" and tmp[1] != "nil":
                        print("Wrong usage of null type", file=sys.stderr)
                        sys.exit(23)

                    types[i - 1] = tmp[0]
                    token[i] = tmp[1]
                else:
                    print(f"Unknown: {token[i]}", file=sys.stderr)
                    sys.exit(23)

def string_serialization(string):
        ascii_code = "\\"
        for i in range(0, len(string)):
            if string[i] == "\\":
                i += 1
                counter = 0
                while i < len(string) and string[i].isnumeric() and counter < 3:
                    ascii_code += string[i]
                    i += 1
                    counter += 1
                if len(ascii_code) != 4:
                    print(f"you have wrong format in ascii code {ascii_code}", file=sys.stderr)
                    sys.exit(23)
                ascii_code = "\\"
        return string

def create_node( token):
        global order
        instruction = ET.SubElement(root, "instruction", order=f"{order}", opcode=f"{token[0]}")
        ET.indent(tree, space=" ", level=0)

        if len(token) == 3 or len(token) == 5 or len(token) == 7:
            arg1 = ET.SubElement(instruction, "arg1", type=f"{token[1 + int((len(token) - 1) / 2)]}")
            ET.indent(tree, space=" ", level=0)
            arg1.text = token[1]

            if len(token) == 5 or len(token) == 7:
                arg2 = ET.SubElement(instruction, "arg2", type=f"{token[2 + int((len(token) - 1) / 2)]}")
                ET.indent(tree, space=" ", level=0)
                arg2.text = token[2]

            if len(token) == 7:
                arg3 = ET.SubElement(instruction, "arg3", type=f"{token[6]}")
                ET.indent(tree, space=" ", level=0)
                arg3.text = token[3]

        order += 1

def switch_case(token):
        if token[0] == "DEFVAR":
            check_validity(token, 2)
            types = ["var"]
            detect_type(token, types)
            token.extend(types)

        elif token[0] == "POPS":
            check_validity(token, 2)
            types = ["var"]
            detect_type(token, types)
            if types[0] != "var":
                print("You only can use variables in POPS call", file=sys.stderr)
                sys.exit(23)
            token.extend(types)

        elif token[0] in ["ADD", "SUB", "MUL", "IDIV", "LT", "GT", "EQ", "AND", "OR", "STRI2INT", "CONCAT", "GETCHAR",
                          "SETCHAR"]:
            check_validity(token, 4)
            types = ["var", "symb", "symb"]
            detect_type(token, types)
            token.extend(types)

        elif token[0] in ["NOT", "INT2CHAR", "STRLEN", "TYPE", "MOVE"]:
            check_validity(token, 3)
            types = ["var", "symb"]
            detect_type(token, types)
            token.extend(types)

        elif token[0] == "READ":
            check_validity(token, 3)
            types = ["var", "type"]
            detect_type(token, types)
            if token[2] not in ["int", "bool", "string"]:
                print("You have wrong type in READ call", file=sys.stderr)
                sys.exit(23)
            token.extend(types)

        elif token[0] == "LABEL":
            check_validity(token, 2)
            types = ["label"]
            name_validity(str(token[1][0]))
            detect_type(token, types)
            token.extend(types)

        elif token[0] in ["JUMP", "CALL"]:
            check_validity(token, 2)
            types = ["label"]
            detect_type(token, types)
            token.extend(types)

        elif token[0] in ["JUMPIFEQ", "JUMPIFNEQ"]:
            check_validity(token, 4)
            types = ["label", "symb", "symb"]
            detect_type(token, types)
            token.extend(types)

        elif token[0] in ["EXIT", "DPRINT", "WRITE", "PUSHS"]:
            check_validity(token, 2)
            types = ["symb"]
            detect_type(token, types)
            token.extend(types)

        elif token[0] in ["BREAK", "RETURN", "POPFRAME", "PUSHFRAME", "CREATEFRAME"]:
            check_validity(token, 1)
            create_node(token)
            return

        else:
            print(f"Unknown instruction: {token[0]}", file=sys.stderr)
            sys.exit(22)

        create_node(token)

def parse():
        empty = True
        for line in sys.stdin:
            if re.search(r'\S', line) and line[0] != "#":
                line = line.split("#")
                if ".IPPcode24" == line[0].split()[0]:
                    empty = False
                    break
                else:
                    print("Something is wrong with the necessary library .IPPcode24", file=sys.stderr)
                    sys.exit(21)
        if empty:
            print("You forgot to include the header", file=sys.stderr)
            sys.exit(21)

        for line in sys.stdin:
            words = line.split()
            new_token = []
            for word in words:
                if "#" in word:
                    word = word.split("#")
                    word = word[0]
                    if word != "":
                        new_token.append(word)
                    break

                new_token.append(word)

            if len(new_token) != 0:
                if new_token[0] == ".IPPcode24":
                    print("Too many headers", file=sys.stderr)
                    sys.exit(23)
                new_token[0] = new_token[0].upper()
                switch_case(new_token)

def xml_create():
    parse()
    tree.write(sys.stdout, xml_declaration=True, encoding="unicode")

def help_info():
    if "--help" in sys.argv:
        if len(sys.argv) > 2:
            sys.exit(10)
        print("""HELP:
                    python3 parse.py < <your_file>""")
        sys.exit(0)
        
if __name__ == "__main__":
    help_info()
    root = ET.Element('program', language="IPPcode24")
    tree = ET.ElementTree(root)
    xml_create()
