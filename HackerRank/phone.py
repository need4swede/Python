
# Given a phone number and a list of words, figure out which of the words can be found within the phone number

# 1 = None
# 2 = abc
# 3 = def
# 4 = ghi
# 5 = jkl
# 6 = mno
# 7 = pqrs
# 8 = tuv
# 9 = wxyz

# Example:

# pNumber = "3552277"
# words = ['foo', 'bar', 'foobar', 'emo', 'cap', 'car', 'cat']

PhoneKeys = dict(
    one = '',
    two = (2, 'abc'),
    three = (3, 'def'),
    four = (4, 'ghi'),
    five = (5, 'jkl'),
    six = (6, 'mno'),
    seven = (7, 'pqrs'),
    eight = (8, 'tuv'),
    nine = (9, 'wxyz')
)

print(PhoneKeys)