import re
import pickle

# Load existing regex expressions
with open('regex_constructor/regex_expressions.pickle', 'rb') as file:
    regex_expressions = pickle.load(file)

added_regex_name = input('Zadajte kľúč asociatívneho pola pre REGEX výraz: ')

def get_user_regex():
    added_regex = input('Zadajte pridávaný REGEX výraz: ')
    try:
        re.findall(added_regex, "test string")
    except Exception:
        print('Zadaný výraz nie je platný REGEX výraz. Skúste to znova')
        get_user_regex()
    print('REGEX výraz je platný')
    return added_regex

added_regex = get_user_regex()

regex_expressions[added_regex_name] = added_regex

with open('regex_constructor/regex_expressions.pickle', 'wb') as file:
    if len(regex_expressions) != 0:
        pickle.dump(regex_expressions, file)
        print('REGEX výrazy boli uložené')



