def get_cot_prompt(prompt: str, language: str = "Python3") -> str:
    example_prompt = """
An accordion is a string (yes, in the real world accordions are musical instruments, but let's forget about it for a while) which can be represented as a concatenation of: an opening bracket (ASCII code $091$), a colon (ASCII code $058$), some (possibly zero) vertical line characters (ASCII code $124$), another colon, and a closing bracket (ASCII code $093$). The length of the accordion is the number of characters in it.

For example, [::], [:||:] and [:|||:] are accordions having length $4$, $6$ and $7$. (:|:), {:||:}, [:], ]:||:[ are not accordions. 

You are given a string $s$. You want to transform it into an accordion by removing some (possibly zero) characters from it. Note that you may not insert new characters or reorder existing ones. Is it possible to obtain an accordion by removing characters from $s$, and if so, what is the maximum possible length of the result?


-----Input-----

The only line contains one string $s$ ($1 \le |s| \le 500000$). It consists of lowercase Latin letters and characters [, ], : and |.


-----Output-----

If it is not possible to obtain an accordion by removing some characters from $s$, print $-1$. Otherwise print maximum possible length of the resulting accordion.


-----Examples-----
Input
|[a:b:|]

Output
4

Input
|]:[|:]

Output
-1

2
1 2

## Let's think step by step and generate code to solve the problem.

```python
# Take user input and assign it to the variable 's'
s = input()

# Calculate the length of the string 's' and assign it to the variable 'n'
n = len(s)

# Initialize variables to store the indices of '[' and ']'
ind = -1
bind = -1

# Variable to track whether '[' or ']' characters have been encountered
f = False

# Step 1: Find the index of the first '[' character after encountering ':'
for i in range(n):
    if s[i] == '[':
        f = True
    elif s[i] == ':':
        if f:
            ind = i
            break

# Reset the flag variable
f = False

# Step 2: Find the index of the last ']' character before encountering ':'
for i in range(n - 1, -1, -1):
    if s[i] == ']':
        f = True
    elif s[i] == ':':
        if f:
            bind = i
            break

# Check conditions to determine if it's possible to obtain an accordion
if ind == -1 or bind == -1:
    # Print -1 if '[' or ']' characters were not found
    print(-1)
elif ind >= bind:
    # Print -1 if the order of '[' and ']' characters is incorrect
    print(-1)
else:
    # Initialize the length of the accordion to 4 (opening and closing brackets, and two colons)
    ans = 4
    # Step 3: Count the number of '|' characters between '[' and ']' indices (inclusive)
    for i in range(ind + 1, bind):
        if s[i] == '|':
            ans += 1
    # Print the calculated length of the resulting accordion
    print(ans)
```

-------

Anton has the integer x. He is interested what positive integer, which doesn't exceed x, has the maximum sum of digits.

Your task is to help Anton and to find the integer that interests him. If there are several such integers, determine the biggest of them. 


-----Input-----

The first line contains the positive integer x (1 ≤ x ≤ 10^18) — the integer which Anton has. 


-----Output-----

Print the positive integer which doesn't exceed x and has the maximum sum of digits. If there are several such integers, print the biggest of them. Printed integer must not contain leading zeros.


-----Examples-----
Input
100

Output
99

Input
48

Output
48

Input
521

Output
499

## Let's think step by step and generate code to solve the problem.

```python
# Take user input as a list of integers representing the digits of the given positive integer x
num = list(map(int, input()))

# Initialize a variable 'best' to store the current best candidate for the maximum sum of digits
best = num[:]

# Step 1: Iterate over the digits in reverse order
for i in range(-1, -len(num) - 1, -1):
    # If the current digit is 0, continue to the next digit
    if num[i] == 0:
        continue
    
    # Decrease the current digit by 1
    num[i] -= 1

    # Step 2: Set all digits to the right of the current digit to 9
    for j in range(i + 1, 0):
        num[j] = 9
    
    # Step 3: Compare the sum of the current number with the sum of the best number
    if sum(num) > sum(best):
        # Update 'best' if the current number has a greater sum
        best = num[:]

# Convert the list of digits to a string, remove leading zeros, and print the result
s = ''.join(map(str, best)).lstrip('0')
print(s)
```

-------

Apart from having lots of holidays throughout the year, residents of Berland also have whole lucky years. Year is considered lucky if it has no more than 1 non-zero digit in its number. So years 100, 40000, 5 are lucky and 12, 3001 and 12345 are not.

You are given current year in Berland. Your task is to find how long will residents of Berland wait till the next lucky year.


-----Input-----

The first line contains integer number n (1 ≤ n ≤ 10^9) — current year in Berland.


-----Output-----

Output amount of years from the current year to the next lucky one.


-----Examples-----
Input
4

Output
1

Input
201

Output
99

Input
4000

Output
1000



-----Note-----

In the first example next lucky year is 5. In the second one — 300. In the third — 5000.

## Let's think step by step and generate code to solve the problem.

```python
def main():
    # Take user input as a string representing the current year in Berland
    s = input()

    # Get the length of the input string (number of digits in the current year)
    n = len(s)

    # Step 1: Create a target lucky year 't' by incrementing the first digit by 1 and padding with zeros
    t = int(str(int(s[0]) + 1) + '0' * (n - 1))

    # Step 2: Calculate the number of years from the current year to the next lucky one
    result = t - int(s)

    # Print the result
    print(result)

# Call the main function
main()
```
"""
    return f"{example_prompt}\n{prompt}\n## Let's think step by step and generate {language} code to solve the problem.\n# ----------------\nImportant: Your response must contain only the {language} code to solve this problem inside ``` block."

@staticmethod
def get_sample_io_str(sample_io: any) -> str:
    sample_io_str = ""
    for i in range(min(len(sample_io['inputs']), len(sample_io['outputs']))):
        input_str = ", ".join([str(x) for x in sample_io['inputs'][i]])
        sample_io_str += f"Input:\n{sample_io['fn_name']}({input_str})\nExpected output:\n{sample_io['outputs'][i]}\n"
    return sample_io_str