#!/usr/bin/python

import os
import subprocess
import time
import progressbar
import sys
import getpass
import random
import getopt
from sys import argv


# Global Variables
iam_user = ""
aws_key_file = ""
aws_profile = "default"
json_output_file = ""
s3_test_file = ""
csv_output_file = ""
new_key = ""
no_key = False
disable_old = False
replace_local_key = False
new_access_key_id = ""
new_secret_key = ""
existing_key_id = ""
aws_pass_env = list()
change_all_passwords = False
create_pass = True
new_pass = ""
user_env = []


# def query_yes_no(question, default="no"):
def query_yes_no(question, default):
    # Yes or no question function
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def get_aws_env():
    global aws_pass_env
    cred_file = os.path.expanduser("~")
    cred_file += "/.aws/credentials"
    r_cred = open(cred_file, 'r')
    for row in r_cred:
        if "aws_access_key_id" in row or "aws_secret_access_key" in row or row == "":
            continue
        elif "[" in row and "]" in row:
            aws_pass_env.append(row.strip())
          #  print row.strip()
          #  aws_pass_env += row
        else:
            continue


def get_username():
    print "Getting account information ........"
    global aws_pass_env, user_env
    for i in aws_pass_env:
        user_env.append(subprocess.check_output("aws iam get-user --query User.UserName --profile " + i.translate(None, '[]'), shell=True))


def show_all_env():
    global aws_pass_env, user_env
    print "Here our your current environments: "

    for u, p in zip(user_env, aws_pass_env):
        print("UserName: " + u.translate(None, '"\n\r')  + "\t\tEnvironment: " + p.translate(None, '[]'))
    #pwlist.append(alphabet[random.randrange(len(alphabet))])
        #print aws_pass_env[i].translate(None, '[]')


def gen_pass():
   alphabet = "abcdefghijklmnopqrstuvwxyz"
   upperalphabet = alphabet.upper()
   special = "!@#$%^&*()[];'?.><,/\=+-"
   pw_len = 0
   divider = 0
   pwlist = []
   rlc = False
   ruc = False
   rqs = False
   rqn = False
   global new_pass
   for u, p in zip(user_env, aws_pass_env):
       print("Getting password requirements for " + p.translate(None, '[]') + " environment.....")
       req_lower_case = subprocess.check_output("aws iam get-account-password-policy --output json --query PasswordPolicy.RequireLowercaseCharacters --profile " + p.translate(None, '[]') , shell=True)
       req_upper_case = subprocess.check_output("aws iam get-account-password-policy --output json --query PasswordPolicy.RequireUppercaseCharacters --profile " + p.translate(None, '[]'),  shell=True)
       min_len = subprocess.check_output("aws iam get-account-password-policy --output json --query PasswordPolicy.MinimumPasswordLength --profile " + p.translate(None, '[]'), shell=True)
       req_num = subprocess.check_output("aws iam get-account-password-policy --output json --query PasswordPolicy.RequireNumbers --profile " + p.translate(None, '[]'), shell=True)
       req_sym = subprocess.check_output("aws iam get-account-password-policy --output json --query PasswordPolicy.RequireSymbols --profile " + p.translate(None, '[]'), shell=True)
       bar = progressbar.ProgressBar()
       for i in bar(range(100)):
           time.sleep(0.02)
       print "Require lowercase: " + req_lower_case + "Require uppercase: " + req_upper_case + "Minimum length: " + min_len + "Require number: " + req_num + "Require special character: " + req_sym
       if pw_len < int(min_len):
           pw_len = int(min_len)
       if "true" in req_lower_case:
           rlc = True
       if "true" in req_upper_case:
           ruc = True
       if "true" in req_sym:
           rqs = True
       if "true" in req_num:
           rqn = True


   if rlc:
       divider += 1
   if rlc:
       divider += 1
   if rqs:
       divider += 1
   if rqn:
       divider += 1

   for i in range(pw_len // divider):
       if rlc:
           pwlist.append(alphabet[random.randrange(len(alphabet))])
       if rlc:
           pwlist.append(upperalphabet[random.randrange(len(upperalphabet))])
       if rqs:
           pwlist.append(special[random.randrange(len(special))])
       if rqn:
           pwlist.append(str(random.randrange(10)))
   for i in range(pw_len - len(pwlist)):
       pwlist.append(alphabet[random.randrange(len(alphabet))])

   random.shuffle(pwlist)
   pwstring = "".join(pwlist)

   print "Generating password based off requirements ......"
   bar = progressbar.ProgressBar()
   for i in bar(range(100)):
       time.sleep(0.06)

   new_pass = pwstring


def change_all_the_passes():
    global create_pass, new_pass
    global aws_pass_env, user_env
    create_pass = query_yes_no("Would you like me to autogenerate a password for you based off your password policy?", "yes")
    if create_pass == False:
        new_pass = getpass.getpass()
        print "You entered: " + new_pass
    else:
        gen_pass()
        for u, p in zip(user_env, aws_pass_env):
            print("Changing password for user: " + u.translate(None, '"\n\r')  + " in aws " + p.translate(None, '[]') + " environment.....")
            bar = progressbar.ProgressBar()
            subprocess.call("aws iam update-login-profile --user-name " + u.translate(None, '"\n\r')  + " --profile " + p.translate(None, '[]') + " --password " + '"%s"'%new_pass, shell=True)
            for i in bar (range(100)):
                time.sleep(0.02)

        print "New password: " + new_pass


        #for i in aws_pass_env:
        #    subprocess.call("aws iam update-login-profile i.translate(None, '[]')
    # aws iam get-account-password-policy --output json --query PasswordPolicy.RequireNumbers


get_aws_env()
get_username()
show_all_env()

change_all_passwords = query_yes_no("Do you want to change password for all your AWS environments?", "yes")

if change_all_passwords == True:
    print "Ok cool, lets change them all"
    change_all_the_passes()
else:
    print "Not changing all passwords"

#print aws_pass_env
#number_of_env = len(aws_pass_env)
#for i in number_of_env:
#print aws_pass_env[0]
#print aws_pass_env[1]
#print aws_pass_env[2]

