import csv
import sys
from pandas import read_csv
from math import floor


def main():

    # Checks the appropriate number of arguments
    if len(sys.argv) != 3:
        sys.exit("Usage: python dna.py data.csv sequence.txt")

    susp = []
    dic = {}
    # Read columns and their names
    with open(sys.argv[1], "r") as file:
        data = read_csv(sys.argv[1])
        keys = list(data.columns)
        reader = csv.DictReader(file)
        reader_c = list(reader)
        for key in keys:
            for row in reader_c:
                susp.append(row[key])
            dic[key] = susp
            susp = []

    # Read DNA sequence
    with open(sys.argv[2], "r") as d_file:
        dna = d_file.readline()
        
    mak = []
    # Loop over each STR
    for i in range(1, len(keys)):
        k = keys[i]
        maks = 0
        # Loop over each letter in dna sequence
        for j in range(len(dna)):
            temp = 0
            if dna[j: j + len(k)] == k:
                temp += 1
                while (dna[j: j + len(k)] == k) and (dna[(j + len(k)): (j + 2*len(k))] == k):
                    temp += 1
                    j += len(k)
                if temp > maks:
                    maks = temp
        mak.insert(i, maks)
    
    # Make a dictionary with matching number of STR
    jail = dic
    i = 0
    for key in keys[1:]:
        for j in range(len(dic[keys[0]])):
            if str(mak[i]) == dic[key][j]:
                jail[key][j] = True
        i += 1
        
    # Make a list with only True value of suspected person
    lists = []
    for i in range(len(dic[keys[0]])):
        temp = {True}
        for key in keys[1:]:
            temp.add(jail[key][i])
        lists.insert(i, temp)
    
    # Final resoults
    m = 0
    for i in range(len(lists)):
        if lists[i] == {True}:
            print(jail[keys[0]][i])
            m = 1
    if m == 0:
        print("No match")
        
        
main()