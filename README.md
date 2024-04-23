# Parse.py

## Usage

python parse.py <path_to_code>

## Program logic

The program begins by creating an XML tree using the ElementTree library. It then calls the main function parse(), which checks if the ".IPPcode24" library was declared correctly and creates an array of tokens for each line of code. This array is then passed to the switch_case() function, which checks, depending on the case, whether the expected number of arguments were provided, adds the expected data types to the array, and checks for various errors using the detect_types() function, which also utilizes the helper functions string_serialization() and name_validity(). If everything went successful, the array is passed to the final function create_node(), which generates an XML node using the ElementTree library.
