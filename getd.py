#! python3
import requests, sys, bs4, re, webbrowser

## GLOBAL VARIABLES
reactions = []
address_search = "https://groups.nscl.msu.edu/jina/reaclib/db/"
address_data = "https://groups.nscl.msu.edu/jina/reaclib/db/flatfile.php?rateindex="

## FUNCTIONS

def read_file(filename):
    with open(filename, 'r') as rFile:
        for line in rFile:
            reactions.append(line)

def get_data():
    for reaction in reactions:
        # Get the rate index from the html-page

        
        # Assumes that the database accepts urls of those given in the txt-file
        print("Attempting to open ", address_search+reaction)
        res = requests.get(address_search+reaction)
        try:
            res.raise_for_status()
        except Exception as exc:
            print("An exception occured for {}: {}".format(reaction, exc))
            continue

        # Find an occurence of the rate index and use it 
        pattern = re.compile("rateindex=(\d+)")
        rateindex = re.search(pattern, res.text)
        if rateindex is None:
            print("Could not find the rate index. Probably unexpected HTML-encoding. Skipping ", reaction)
            continue
        print("Found the rate index. Downloading data")

        # Get the data
        res = requests.get(address_data+str(rateindex.group(1))+"&flattype=4")
        try:
            res.raise_for_status()
        except Exception as exc:
            print("An exception occured for {}: {}".format(reaction, exc))
            continue

        wFile = open(reaction+".txt", 'wb')
        for chunk in res.iter_content(100000):
            wFile.write(chunk)
        wFile.close()

        
        

## MAIN

if __name__ == "__main__":
    if len(sys.argv) > 1:
        read_file(str(sys.argv[1]))
        get_data()
    else:
        print("Expected file argument: getd.py reactions.txt")
