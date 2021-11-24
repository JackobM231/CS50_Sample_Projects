
x = input("Text: ")
l = 0  # Number of letters
w = 1  # Number of words
s = 0  # Number of sentences


for i in range((len(x))):
    if x[i].isalpha():
        l += 1
    elif x[i] == " ":
        w += 1
    elif x[i] in "!.?":
        s += 1

L = (l * 100) / w
S = (s * 100) / w
index = 0.0588 * L - 0.296 * S - 15.8
grade = round(index)

# Final resolt
if index >= 16:
    print("Grade 16+")

elif index < 1:
    print("Before Grade 1")
    
else:
    print(f"Grade {grade}")