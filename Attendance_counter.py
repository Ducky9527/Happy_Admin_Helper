import pandas as pd

"""
dataframe structure of the csv I will be using here.

std_id, last name, first name, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12

"""

df = pd.read_csv('Attendence.csv')
df['Attendance'] = (df.iloc[:, 1:].applymap(lambda x: str(x).strip().upper()) == 'Y' ).sum(axis=1)

"""
lambda x: str(x).strip.upper()

lambda here is a 'one off' function.

It is essentially a function that looksl like this: 

def f(x):
    result = str(x).strip().upper()
    return result


str(x) 
Convert all the cell's value to a string
This is especially important when some of the cells are empty (NaN).
I don't want to compute empty cells, so I need to make sure my code reads the cell as string.

.strip()
remove leading and tailing whitespace, in case students accidentally left some spaces on the attendance sheet...

.upper()
convert all the string to upper case


.sum(axis=1)
axis=1 gives a row-wise sum

Here, if I change the numner from 1 to 0, I will get a 'column-wise sum'.
There's no axis=2.
"""

df['Score'] = df['Attendance'].map(lambda x: 10 if x >=5 else x * 2) # create a column for attendance score; 1 for 2 points, and max 10 from attendance.

"""
lambda x:10 if x >=5 else x *2

def f(x):
    if x >= 5:
        score = 10
    else:
        score = x *2

    return score
"""

df.to_csv('Final_attendance.csv', index=False)

"""
Second part of the code - in case you care how many students attended the tutorial more than 5 times.
"""


df = pd.read_csv('Admin/Final_attendance.csv')

num_std = (df['Attendance'] > 5).sum() #feel free to change the number 5 into any number
no_show = (df['Attendance'] == 0).sum() #count how many have never shown up in tutorials

"""
.sum() = .sum(axis=0)
Which means 'column-wise sum.
"""

print(num_std) # the result will be shown in your terminal.
print(no_show)
