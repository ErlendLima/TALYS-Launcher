#! python3

"""
This script finds and downloads data from two libraries for reaction rates.
These libraries are REACLIB and BRUSLIB. As the websites do not supply an easy
way of requesting the data, the script uses URL-manipulation and HTML-scraping
to find the download-link. As the reader might suspect, this method will fail
if the websites are either updated or suddenly uses another format for their
URLs. Hopefully, the script is simple enough to change should the need arise.

For input, the script requires a file containing the reactions for which data
shall be retrieved. The format is #PROTONS SYMBOL #NEUTRONS. In addition
to this, a range can be specified by adding the terminative value at the end, such as fe67(ng) 71
or 26fe41 45. The file should look like

63eu96 103
26fe41

NOTE: In order to use BRUSLIB, the second format must be used, while REACLIB
can use both.

The output files are named after each reaction and suffixed with the library
from which it was downloaded.

The syntax for the script is
python getd.py inputfile library
"""

import requests, sys, bs4, re, argparse

## GLOBAL VARIABLES
address_search = "https://groups.nscl.msu.edu/jina/reaclib/db/"
address_data = "https://groups.nscl.msu.edu/jina/reaclib/db/flatfile.php?rateindex={}&flattype=4"
address_bruslib = "http://www.astro.ulb.ac.be/bruslib/cgi/reacRate.cgi?nameofNOPReacRates={}&nameofNONReacRates={}&SubmitMess=Submit&PchosenIdx=0&NchosenIdx=0"


## FUNCTIONS

_nsre = re.compile('([0-9]+)')
def natural_sort_key(s):
    # Sorts alphanumerically
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(_nsre, s)]

def write(string):
    """ Simple function to print without newline """
    sys.stdout.write(string)
    sys.stdout.flush()

def save_data(filename, link):
    """ Requests data from the link and saves it to the filename """
    res = scrape(link)
    if res is None:
        return False
    
    write("Saving to {}...".format(filename))
    try:
        wFile = open(filename, 'wb')
        for chunk in res.iter_content(100000):
            wFile.write(chunk)
            wFile.close()
    except Exception as exc:
        print(exc)
        return False
    print("ok")
    return True

def read_file(filename):
    """ Reads the input file and checks the format """
    reactions_reaclib = []
    reactions_bruslib = []
    #format_reaclib = re.compile("\w\w?(\d{1,3})\(\w,\w\)(\w\w?\d{1,3})?\s?(\d{1,3})?")
    format_bruslib = re.compile("(\d{1,3})(\w\w?)(\d{1,3})\s?(\d{1,3})?")
    with open(filename, 'r') as rFile:
        for line in rFile:
            line = line.rstrip()
            match = re.match(format_bruslib, line)
            if match is not None:
                # Iterate over the range, if given
                start = int(match.group(3))
                end = int(match.group(4))+1 if match.group(4) is not None else start+1
                for neutrons in range(start, end):
                    reactions_bruslib.append([match.group(1),
                                              match.group(2), neutrons])
                    for process in ["(n,g)"]: #, "(n,p)", "(n,a)"]: <------Uncomment this for more reactions                                 
                        # Convert to reaclib format                                        
                        reaction =  "{}{}{}".format(match.group(2),                    
                                                    int(match.group(1))+int(neutrons), 
                                                    process)                               
                        reactions_reaclib.append(reaction)                                 
            else:
                print("{} is of invalid format".format(line))
    print("Parsed {} reactions, where {} can be used for BRUSLIB".format(
        len(reactions_reaclib), len(reactions_bruslib)))
    # Remove duplicates
    reactions_reaclib = list(set(reactions_reaclib))
    reactions_reaclib.sort(key=natural_sort_key)
    return reactions_reaclib , reactions_bruslib

def scrape(address):
    """ Get HTML-page for the given url """
    try:
        res = requests.get(address)
        res.raise_for_status()
    except Exception as e:
            print("An exception occured: {}".format(e))
            return None
    return res

    
def get_REACLIB(reactions):
    """ Get data from REACLIB. Finds the rateindex and uses it to download the
    data """
    for reaction in reactions:
        # Get the rate index from the html-page
        write("Attempting to open "+address_search+reaction+"...")
        res = scrape(address_search+reaction)
        if res is None:
            continue
        print("ok")

        # Find an occurence of the rate index and use it 
        pattern = re.compile("rateindex=(\d+)")
        rateindex = re.search(pattern, res.text)
        if rateindex is None:
            print("Could not find the rate index. Probably unexpected HTML-encoding. Skipping ", reaction)
            continue

        # Get the data
        print("Found the rate index. Attempting to download data")
        link = address_data.format(rateindex.group(1))
        filename = "{}_reaclib.txt".format(reaction)
        if not save_data(filename, link):
            continue

def get_BRUSLIB(reactions):
    """ Get data from BRUSLIB """
    pattern = re.compile("data for Proton Reaction Rates")
    for reaction in reactions:
        # Attempt to open the HTML-page
        address = address_bruslib.format(reaction[0], reaction[2])
        write("Attempting to open BRUSLIB for {}{}{}...".format(reaction[0],
                                                                reaction[1], reaction[2]))
        res = scrape(address)
        if res is None:
            continue
        print("ok")

        # Look for the link to the data
        write("Looking for link...")
        soup = bs4.BeautifulSoup(res.text, "html.parser")
        link_to_data = "http://www.astro.ulb.ac.be/bruslib/"
        for link in soup.findAll('a'):
            if link.contents[0] == "data for Neutron Reaction Rates":
                link_to_data += link.get('href')[2:]
                break
        print("ok")

        # Download and save the data
        filename = "{}{}{}_bruslib.txt".format(reaction[0], reaction[1], reaction[2])
        if not save_data(filename, link_to_data):
            continue

## MAIN

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="File containing the reactions")
    parser.add_argument("database", help="The database to search",
                        choices=["REACLIB", "BRUSLIB"], type=str.upper)
    args = parser.parse_args()
    reactions = read_file(args.input)
    if args.database == "REACLIB":
        get_REACLIB(reactions[0])
    elif args.database == "BRUSLIB":
        get_BRUSLIB(reactions[1])
    else:
        print("Expected file argument: getd.py reactions.txt")
