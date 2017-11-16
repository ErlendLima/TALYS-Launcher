#! python3

"""
This script finds and downloads data from three libraries for reaction rates.
These libraries are REACLIB, BRUSLIB and EXFOR. As the websites do not supply
an easy way of requesting the data, the script uses URL-manipulation,
HTML-scraping and website interaction to find the download link. As the
reader might suspect, this method will fail if the websites are either
updated or suddenly uses another format for their URLs.
Hopefully, the script is simple enough to change should the need arise.

For input, the script requires a file containing the reactions for which data
shall be retrieved. There are two formats available:
1) The same json-file as used for talys.py
2) A file consisting of lines of the format #PROTONS SYMBOL #NEUTRONS.
   In addition to this, a range can be specified by adding the terminative
   value at the end, such as fe67(ng) 71 or 26fe41 45.

   If this file is to be used with EXFOR, add the lines
   E1 <mininum energy [MeV]>
   E2 <maximum energy [MeV]>
   in order to define an energy range.

   Beneath is an example of how a file could look like:

        63eu96 103
        26fe41

        E1 2.5E-6
        E2 0.05E-3

The output files are named after each reaction and suffixed with the library
from which it was downloaded.

If one wants to download data from EXFOR, the package slinter is required.
In addition, Google Chrome must be installed and updated to the newest
version, and the newest chromedriver must be installed.
See https://splinter.readthedocs.io/en/latest/drivers/chrome.html for
more information and installtion instructions

The syntax for the script is
python getd.py inputfile library
"""

import requests, sys, bs4, re, argparse, os, time
from readers import Json_reader, BRUSLIB_reader

## GLOBAL VARIABLES
address_search = "https://groups.nscl.msu.edu/jina/reaclib/db/"
address_data = "https://groups.nscl.msu.edu/jina/reaclib/db/flatfile.php?rateindex={}&flattype=4"
address_bruslib = "http://www.astro.ulb.ac.be/bruslib/cgi/reacRate.cgi?nameofNOPReacRates={}&nameofNONReacRates={}&SubmitMess=Submit&PchosenIdx=0&NchosenIdx=0"
address_bruslib_data = "http://www.astro.ulb.ac.be/bruslib/"
address_exfor_search = "http://www.nndc.bnl.gov/exfor/exfor.htm"

Z_nr = {'H': '001',  'He': '002', 'Li': '003',  'Be': '004', 'B': '005',   'C': '006',  'N': '007',   'O': '008',  'F': '009',  'Ne': '010',
        'Na': '011', 'Mg': '012', 'Al': '013',  'Si': '014', 'P': '015',   'S': '016',  'Cl': '017',  'Ar': '018', 'K': '019',  'Ca': '020',
        'Sc': '021', 'Ti': '022', 'V': '023',   'Cr': '024', 'Mn': '025',  'Fe': '026', 'Co': '027',  'Ni': '028', 'Cu': '029', 'Zn': '030',
        'Ga': '031', 'Ge': '032', 'As': '033',  'Se': '034', 'Br': '035',  'Kr': '036', 'Rb': '037',  'Sr': '038', 'Y': '039',  'Zr': '040',
        'Nb': '041', 'Mo': '042', 'Tc': '043',  'Ru': '044', 'Rh': '045',  'Pd': '046', 'Ag': '047',  'Cd': '048', 'In': '049', 'Sn': '050',
        'Sb': '051', 'Te': '052', 'I': '053',   'Xe': '054', 'Cs': '055',  'Ba': '056', 'La': '057',  'Ce': '058', 'Pr': '059', 'Nd': '060',
        'Pm': '061', 'Sm': '062', 'Eu': '063',  'Gd': '064', 'Tb': '065',  'Dy': '066', 'Ho': '067',  'Er': '068', 'Tm': '069', 'Yb': '070',
        'Lu': '071', 'Hf': '072', 'Ta': '073',  'W': '074',  'Re': '075',  'Os': '076', 'Ir': '077',  'Pt': '078', 'Au': '079', 'Hg': '080',
        'Tl': '081', 'Pb': '082', 'Bi': '083',  'Po': '084', 'At': '085',  'Rn': '086', 'Fr': '087',  'Ra': '088', 'Ac': '089', 'Th': '090',
        'Pa': '091', 'U': '092',  'Np': '093',  'Pu': '094', 'Am': '095',  'Cm': '096', 'Bk': '097',  'Cf': '098', 'Es': '099', 'Fm': '100',
        'Md': '101', 'No': '102', 'Lr': '103',  'Rf': '104', 'Db': '105',  'Sg': '106', 'Bh': '107',  'Hs': '108', 'Mt': '109', 'Ds': '110',
        'Rg': '111', 'Cn': '112', 'Uut': '113', 'Fl': '114', 'Uup': '115', 'Lv': '116', 'Uus': '117', 'Uuo': '118'}

## FUNCTIONS

_nsre = re.compile('([0-9]+)')
def natural_sort_key(s):
    """ Sorts alphanumerically

    Parameters: s: the string to be sorted
    Returns:    A list over the sorted string
    Algorithm:  Use regex to split a string with numbers as delimiters,
                turn letters to lowercase and digits to ints, and return a
                list over the resulting values
    """
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(_nsre, s)]


def write(string):
    """ Simple function to print without newline

    Parameters: string: the string to be written to screen
    Returns:    None
    Algorithm:  Use sys to write to the screen and flush
    """
    sys.stdout.write(string)
    sys.stdout.flush()


def save_data(filename, link):
    """ Requests data from the link and saves it to the filename

    Parameters: filename: the name of the file to be saved
                link:     the url to download from
    Returns:    1 if successful, 0 if not
    Algorithm:  Call scrape(link) to fetch the data, then write it to the file
                in chunks in binary mode. Any exception makes the function
                return 0"""

    res = scrape(link)
    if res is None:
        return False
    
    write("Saving to {}...".format(filename))
    try:
        with open(filename, 'wb') as wFile:
            # Write in chunks of of 10Kb (?)
            for chunk in res.iter_content(100000):
                wFile.write(chunk)
    except Exception as exc:
        print("Error:", exc)
        return False
    print("ok")
    return True


def scrape(address):
    """ Get HTML-page for the given url

    Parameters: address: the address to fetch the HTML-page from
    Returns:    requests-object if successful, else None
    Algorithm:  Simple wrapper for requests.get(address)
    """
    try:
        res = requests.get(address)
        res.raise_for_status()
    except Exception as e:
        print("An exception occured: {}".format(e))
        return None
    return res


def change_directory(library):
    """ Creates and moves working directory to decrease clutter

    Parameters: library: the name of the library to collect data from
    Returns:    None
    Algorithm:  The name is created by the date, time and library.
                If the name does not exist, create it.
    """
    date_dir = time.strftime('%y%m%d')
    time_dir = time.strftime('%H%M%S')
    directory = "{}-reaction-rates-{}-{}".format(library, date_dir, time_dir)
    if not os.path.exists(directory):
        os.makedirs(directory)
        os.chdir(directory)


def get_REACLIB(reader):
    """ Get data from REACLIB

    Parameters: reader: a Basic_reader object
    Returns:    None
    Algorithm:  Convert the Basic_reader to be compatible with REACLIB, open
                the REACLIB website, search for the rateindex (a number that
                identifies the reaction) and downloads the data
    """

    # Create a list over reactions compatible with REACLIB
    reactions = []
    for element in reader.keywords["element"]:
        for mass in reader.keywords["mass"][element]:
            reactions.append("{}{}(n,g)".format(element, mass))

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
        filename = "{}_reaclib.txt".format(reaction[:-5])
        if not save_data(filename, link):
            continue


def get_BRUSLIB(reader):
    """ Get data from BRUSLIB

    Parameters: reader: a Basic_reader object
    Returns:    None
    Algorithm:  Convert Basic_reader to BRUSLIB-format, open the HTML-page,
                parse the page, find the link to the download page and
                save the result.
    """

    # Create a list over reactions compatible with BRUSLIB
    reactions = []
    for element in reader.keywords["element"]:
        for mass in reader.keywords["mass"][element]:
            protons = int(Z_nr[element])
            reactions.append([protons, element, mass-protons])

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
        link_to_data = address_bruslib_data
        for link in soup.findAll('a'):
            if link.contents[0] == "data for Neutron Reaction Rates":
                link_to_data += link.get('href')[2:]
                break
            print("ok")

        # Download and save the data
        filename = "{}{}{}_bruslib.txt".format(reaction[0], reaction[1], reaction[2])
        if not save_data(filename, link_to_data):
            continue


def get_EXFOR(reader):
    """ Get data from EXFOR

    Parameters: reader: a Basic_reader object
    Returns:    None
    Algorithm:  Open the database's website in Google Chrome, manipulate
                the search options and run the search. Look on the resulting
                page for clues on wether it was successful. If it was,
                download all of the results
    """
    from splinter import Browser

    # Make sure the values aren't rounded off
    energy_min = "{:.7f}".format(reader["E1"])
    energy_max = "{:.7f}".format(reader["E2"])
    # test case # reader = {"element":["Nd"], "mass":{"Nd":[150]}}
    with Browser('chrome') as browser:
        for element in reader["element"]:
            for mass in reader["mass"][element]:
                write("Searching for {}{}...".format(mass, element))
                # Open the page
                browser.visit(address_exfor_search)
                # Check the checkbox for "Target"
                browser.check("chkTarget")
                # Fill in the search term
                browser.fill("Target", '{}-{}'.format(element, mass))
                # Repeat for the next forms
                browser.check("chkReaction")
                browser.fill("Reaction", "n,g")
                browser.check("chkEnergyMin")
                browser.fill("EnergyMin", energy_min)
                browser.check("chkEnergyMax")
                browser.fill("EnergyMax", energy_max)
                # Choose energy unit
                browser.find_by_xpath(".//*[contains(text(), 'MeV')]").click()
                # Click submit
                browser.find_by_xpath("/html/body/form/table/tbody/tr/td[1]/table/tbody/tr[17]/td[3]/input[1]").click()
                if browser.is_text_present("NO DATA FOUND"):
                    print("not found")
                    continue
                else:
                    print("ok")
                    # Select all unselected
                    browser.find_by_xpath("/html/body/form[1]/input[3]").click()
                    # Retrieve
                    browser.find_by_xpath("/html/body/form[1]/input[1]").click()
                    url = browser.find_link_by_text("X4Out").first['href']
                    filename = "{}{}(n,g)_exfor.txt".format(mass, element)
                    save_data(filename, url)


## MAIN

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="File containing the reactions")
    parser.add_argument("database", help="The database to search",
                        choices=["REACLIB", "BRUSLIB", "EXFOR"],
                        type=str.upper)
    args = parser.parse_args()

    if "json" in args.input:
        # If the file is a json-file, parse it as a json file
        write("Reading JSON-file...")
        reader = Json_reader(args.input)
    else:
        # else, use the format described above
        write("Reading reactions-file...")
        reader = BRUSLIB_reader(args.input)
    print("ok")

    if args.database == "REACLIB":
        change_directory("REACLIB")
        get_REACLIB(reader)
    elif args.database == "BRUSLIB":
        change_directory("BRUSLIB")
        get_BRUSLIB(reader)
    elif args.database == "EXFOR":
        change_directory("EXFOR")
        get_EXFOR(reader)
