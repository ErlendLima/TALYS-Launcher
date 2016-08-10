import os
import shutil

def import_options():
    """ Import the the options. Returns the options in a dict """

    import talys_options

    user_input_keys = []
    user_input_values = []
    for key, value in talys_options.__dict__.items():
        if '__' not in key:
            user_input_keys.append(key)
            user_input_values.append(value)

    user_input_dict = dict(zip(user_input_keys, user_input_values))
    return user_input_dict


options = import_options()
for element in options["element"].split(','):
    element = element.strip()
    if not os.path.exists(str(element)):
        os.makedirs(str(element))

#    shutil.copy("jobscript", str(element))
    shutil.copy("talys.py", str(element))
    wFile = open(os.path.join(str(element), "talys_options.py"), "w")
    with open("talys_options.py", "r") as rFile:
        for line in rFile:
            if line.startswith("element"):
                wFile.write("element = '{}'".format(element))
            else:
                wFile.write(line)
    wFile.close()
