# Thanks to Jason Ostrom for creating this Terraform generator to generate an emulation framework
# Create an Azure Sentinel deployment with Azure VMs shipping logs to Sentinel Log Analytics Workspace!
# Optionally, create a full blown AD environment with Domain Join and logged in users 
# This script helps you to automatically and quickly write terraform
# From there you can customize your terraform further and create your own templates!
# Author:  Jason Ostrom

from faker import Faker
import random
import argparse
import os
import subprocess
import urllib.request
import secrets
import string
import logging
from csv import reader
import os.path
import linecache


# Override whitelist means that it will try to auto-detect the public IP address and override the whitelist_nsg variable
# If override is true, it tries to find public IP address automatically
# If you don't want this, set it to false and you can control the whitelist IP address with 'whitelist_nsg" variable 
override_whitelist = True 

# Azure NSG
# By default, allow all IP addresses for Azure NSGs
whitelist_nsg = "*"

# logfile configuration
logging.basicConfig(format='%(asctime)s %(message)s', filename='ranges.log', level=logging.INFO)

# The instance size for each system
size_win10 = "Standard_D2as_v4"
size_dc = "Standard_D2as_v4"

# dc_ip - The domain controller IP address
dc_ip = ""

####
# Functions
####
def get_random_user(csv_file):
    # get line count
    with open(csv_file, 'r') as fp:
        for count, line in enumerate(fp):
            pass

    random_choice = random.randint(2, count)

    myline = linecache.getline(csv_file, random_choice, module_globals=None)
    elements = myline.split(",")
    full_name = elements[0]
    username = elements[1].split("@")[0]
    password = elements[2]
    return (full_name, username, password)

    csv_file.close()

def get_winrm_user(csv_file):

    with open(csv_file, 'r') as csv_object:
        csv_reader = reader(csv_object)
        header = next(csv_reader)

        if header != None:
            for row in csv_reader:

                da_value = row[5]
                ## get the first domain admin where da is set to True
                if da_value.upper() == "TRUE":

                    username = row[1].split("@")[0]
                    password = row[2]
                    return(username, password)

    return False

# Check the user supplied csv file for correctness
def check_ad_csv(csv_file):

    retval = True
    da_set = False

    if not os.path.exists(csv_file):
        print("[-] File doesn't exist: ",csv_file)
        print("[-] Going to exit")
        return False

    with open(csv_file, 'r') as csv_object:
        csv_reader = reader(csv_object)
        header = next(csv_reader)
        # Check 1: Check the header
        if len(header) == 6 and header[0] == 'name' and header[1] == 'upn' and header[2] == 'password' and header[3] == 'groups' and header[4] == 'oupath' and header[5] == 'domain_admin':
            # All good - do nothing
            pass
        else:
            print("    [-] Incorrect CSV header")
            print("    [-] This is the parsed header: ",header)
            print("    [-] Example of a good header:  name,upn,password,groups,oupath,domain_admin")
            return False
        example_row = "Olivia Odinsdottir,oliviaodinsdottir@rtcfingroup.com,MyPassword012345,IT,OU=IT;DC=rtcfingroup;DC=com,True"
        count = 1
        if header != None:
            for row in csv_reader:
                count+=1
                # Check 1: 6 fields in each row
                row_length = len(row)
                if row_length != 6:
                    print("    [-] Error: The row must have 6 fields")
                    print("    [-] Error: Actual fields: ", row_length)
                    print("    [-] Error found at line ", count)
                    print("    [-] Bad parsed row: ",row)
                    print("    [-] Example good row: ",example_row)
                    print("    [-] Going to exit")
                    return False

                # Check 2: No blank data fields
                for element in row:
                    if element == "":
                        print("    [-] Error: Blank data field found!")
                        print("    [-] Error found at line ", count)
                        print("    [-] Bad parsed row: ",row)
                        print("    [-] Example good row: ",example_row)
                        print("    [-] Going to exit")
                        return False

                # Check 3: Check oupath to be proper
                # Check 3: Check that AD Group is included in oupath
                oupath_string = row[4]
                oupath = oupath_string.split(";")
                if len(oupath) == 3:
                    pass
                else:
                    print("    [-] Error found at line ", count)
                    print("    [-] Error:  OUPath will cause errors loading AD")
                    print("    [-] Error:  Expected three ; delimited fields")
                    print("    [-] Error:  Invalid: ",oupath_string)
                    print("    [-] Error:  Valid example: OU=IT;DC=rtcfingroup;DC=com")
                    print("    [-] Going to exit")
                    return False
                ad_group = row[3]
                ou_ad_group = ""
                oustring = oupath_string.split(";")[0]
                if "OU=" not in oustring:
                    print("    [-] Error in OU field")
                    print("    [-] Error found at line ", count)
                    print("    [-] Error: didn't find 'OU='")
                    print("    [-] Error:  Invalid: ", oustring)
                    print("    [-] Error:  Valid example: OU=IT")
                    print("    [-] Going to exit")
                    return False
                else:
                    ou_parsed = oustring.split("=")
                    if len(ou_parsed) == 2:
                       ou_ad_group = ou_parsed[1]
                    else:
                        print("    [-] Error in OU field")
                        print("    [-] Error found at line ", count)
                        print("    [-] Error:  Invalid: ", oustring)
                        print("    [-] Error:  Valid example: OU=IT")
                        print("    [-] Going to exit")
                        return False

                if ad_group == ou_ad_group:
                    pass
                else:
                    print("    [-] Error matching AD group with oupath")
                    print("    [-] Error found at line ", count)
                    print("    [-] AD will not correctly build with users, groups, and OU")
                    print("    [-] The AD group value and OU= must match for user to be correctly placed into AD Group and OU")
                    print("    [-] AD Group: ",ad_group)
                    print("    [-] OUPath AD group: ",ou_ad_group)
                    print("    [-] oupath: ", oupath_string)
                    print("    [-] Valid example:  Regina Perkins,reginaperkins@rtcfingroup.com,MyPassword012345,Marketing,OU=Marketing;DC=rtcfingroup;DC=com,False")
                    print("    [-] To bypass this strict check, you can set retval to True in script")
                    retval = False

                # Check 4: OUPath doesn't match for AD Domain you are going to build
                # only check if the ad_domain is set
                if args.ad_domain:
                    dc1_splits = oupath[1].split("=")
                    dc1 = dc1_splits[1]
                    dc2_splits = oupath[2].split("=")
                    dc2 = dc2_splits[1]
                    dc_domain = dc1 + "." + dc2
                    if args.ad_domain == dc_domain:
                        # we are good, they match
                        pass
                    else:
                        print("    [-] Error matching oupath domain with --ad_domain value")
                        print("    [-] AD users, groups, or OUs will not be correctly built unless this matches")
                        print("    [-] Error found at line ", count)
                        print("    [-] ad_domain value: ",args.ad_domain)
                        print("    [-] domain from oupath: ",dc_domain)
                        print("    [-] oupath value: ",oupath)
                        print("    [-] To bypass this strict check, you can set retval to True in script")
                        retval = False

                # Check 5: At least one DA is set
                if da_set:
                    pass
                else:
                    da_value = row[5]
                    if da_value.upper() == "TRUE":
                        da_set = True

                # Check 6: Either True or False for domain admin
                da_value = row[5]
                if not da_value.upper() == "TRUE" and not da_value.upper() == "FALSE":
                    print("    [-] Error domain admin value must be True or False")
                    print("    [-] Error found at line ", count)
                    print("    [-] Value: ", da_value)
                    print("    [-] Example: Olivia Odinsdottir,oliviaodinsdottir@rtcfingroup.com,MyPassword012345,IT,OU=IT;DC=rtcfingroup;DC=com,True")
                    return False

                # Check 7: upn for each user matches domain
                if args.ad_domain:
                    upn_domain = row[1].split("@")[1]
                    if upn_domain == args.ad_domain:
                        pass
                    else:
                        print("    [-] Error: upn domain doesn't match --ad_domain value")
                        print("    [-] Error: This will prevent users from being added to AD")
                        print("    [-] Error found at line ", count)
                        print("    [-] upn domain value:",upn_domain)
                        print("    [-] --ad_domain value:", args.ad_domain)
                        print("    [-] To bypass this strict check, you can set retval to True in script")
                        retval = False

    # check if at least one Domain Admin is set
    if da_set:
        pass
    else:
        print("    [-] Error:  At least one domain admin is required for Domain Join")
        print("    [-] Error:  This is set in the CSV at the last field")
        print("    [-] Error:  Set at least one user to True")
        print("    [-] Example: Olivia Odinsdottir,oliviaodinsdottir@rtcfingroup.com,MyPassword012345,IT,OU=IT;DC=rtcfingroup;DC=com,True")
        print("    [-] To bypass this strict check, you can set retval to True in script")
        retval = False

    # final return
    return retval

### automatically find pubblic IP address and return it if found 
def check_public_ip_addr():
    try:
        ext_ip = urllib.request.urlopen('http://ifconfig.so').read().decode('utf8')
        print("[+] Public IP address detected: ", ext_ip)
        logging.info('[+] Public IP address detected: %s', ext_ip)
        return ext_ip
    except:
        print("An error occured with urllib")

if override_whitelist:
    retval = check_public_ip_addr()
    if not retval: 
        pass
        # Something went wrong so set default to *
    else:
        print("[+] Setting Azure NSG Whitelist to: ", retval)
        logging.info('[+] Setting Azure NSG Whitelist to: %s', retval)
        whitelist_nsg = retval
# End Azure NSG Whitelist section

# argparser stuff
parser = argparse.ArgumentParser(description='A script to create Sentinel deployment with optional VMs')

# Add argument for count of Windows 10 Pro endpoints 
parser.add_argument('-e', '--endpoints', dest='endpoints_count')

# Add argument for resource group name 
parser.add_argument('-r', '--resource_group', dest='resource_group')

# Add argument for location 
parser.add_argument('-l', '--location', dest='location')

# Add argument for enabling Domain Controller 
parser.add_argument('-dc', '--domain_controller', dest='dc_enable', action='store_true')

# Add argument for Active Directory Domain 
parser.add_argument('-ad', '--ad_domain', dest='ad_domain')

# Add argument for Active Directory Users count 
parser.add_argument('-au', '--ad_users', dest='user_count')

# Add argument for user supplied CSV to load Active Directory
parser.add_argument('-cs', '--csv', dest='user_csv')

# Add argument for  Local Administrator 
parser.add_argument('-u', '--admin', dest='admin_set')

# Add argument for password  
parser.add_argument('-p', '--password', dest='password_set')

# Add argument for domain_join 
parser.add_argument('-dj', '--domain_join', dest='domain_join', action='store_true')

# Add argument for auto login 
parser.add_argument('-al', '--auto_logon', dest='auto_logon', action='store_true')

# Add argument for enabling Office 365 data connector
parser.add_argument('-odc', '--data_connector_office', dest='odc_enable', action='store_true')

# Add argument for enabling Azure AD logs data connector
parser.add_argument('-adc', '--data_connector_aad', dest='adc_enable', action='store_true')

# parse arguments
args = parser.parse_args()

# get Local Admin 
default_input_admin = ""
if args.admin_set:
    default_input_admin= args.admin_set
    print("[+] Local Admin account name:  ",default_input_admin)
    logging.info('[+] Local Admin account name: %s', default_input_admin)

# get input password
default_input_password = ""
if args.password_set:
    default_input_password = args.password_set
    print("[+] Password desired for all users:  ",default_input_password)
    logging.info('[+] Password desired for all users: %s', default_input_password)

#### Create Extra AD Users if desired
# Convert desired user count to integer
# counter for users added to the list
users_added = 0

def get_password():

    #length of password
    length = 10 

    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    num = string.digits
    all = lower + upper + num

    # create blank password string / array
    password = []
    # at least one lower
    password.append(random.choice(lower))
    # at least one upper
    password.append(random.choice(upper))
    # at least one number 
    password.append(random.choice(num))
    for i in range(1, length - 2):
        if len(password) < length:
            password.append(random.choice(all))

    random.shuffle(password)

    final_random_password = ''.join(password)

    if args.password_set:
        return default_input_password 
    else:
        return final_random_password 

#### ACTIVE DIRECTORY CONFIGURATION
### Default Domain / Default AD Domain
ad_users_csv = "ad_users.csv"
default_aduser_password = get_password() 
default_domain = "rtc.local"
default_winrm_username = ""
default_winrm_password = get_password() 
default_admin_username = "RTCAdmin"
default_admin_password = get_password() 
default_da_password = get_password() 
ad_groups = ["Marketing", "IT", "Legal", "Sales", "Executive", "Engineering"]

# Get the default domain if specified
if args.ad_domain:
    default_domain = args.ad_domain
    print("[+] Setting AD Domain to build AD DS:",default_domain)
    logging.info('[+] Setting AD Domain to build AD DS: %s', default_domain)
# Get the Admin account if specified
if args.admin_set:
    default_admin_username = args.admin_set

# duplicate count for created AD users
duplicate_count = 0

if args.user_count and args.user_csv:
    print("[-] Both --ad_users and --csv are enabled ~ Please choose one")
    exit()

# Extra AD users beyond the default in default_ad_users
extra_users_list = [] 
all_ad_users = []
if args.user_count:
    duser_count = int(args.user_count)

    ### Generate a user's name using Faker
    ### Insert the user into a list only if unique
    ### Loop until the users_added equals desired users
    print("[+] Creating unique user list")
    logging.info('[+] Creating unique user list')
    while users_added < duser_count:
        faker = Faker()
        first = faker.unique.first_name()
        last = faker.unique.last_name()
        display_name = first + " " + last
        if display_name in extra_users_list:
            print("    [-] Duplicate user %s ~ not adding to users list" % (display_name))
            logging.info('[-] Duplicate user %s', display_name)
            duplicate_count+=1
        else:
            extra_users_list.append(display_name)
            user_dict = {"name":"", "pass":""}
            user_dict['name'] = display_name 
            user_dict['pass'] = default_aduser_password 
            all_ad_users.append(user_dict)
            users_added+=1

    print("[+] Number of users added into list: ",len(extra_users_list))
    logging.info('[+] Number of users added into list %d', len(extra_users_list))
    print("[+] Number of duplicate users filtered out: ",duplicate_count)
    logging.info('[+] Number of duplicate users filtered out: %s', duplicate_count)
### End of extra AD Users

### Check the user supplied CSV for issues
### Check the file that is going to load Active Directory users, groups, OUs
if args.user_csv:
   print("[+] User supplied CSV file for Active Directory users: ",args.user_csv)
   print("[+] Checking the file to make sure users will load into AD")
   # Check the user supplied AD csv file to make sure it is properly built to work
   retval = check_ad_csv(args.user_csv)
   if retval:
       print("    [+] The file looks good")
   else:
       print("    [+] Exit due to csv file not looking good")
       exit()


# Parsing some of the arguments
if not args.endpoints_count:
    print("[+] Windows 10 Pro Endpoints: 0")
    logging.info('[+] Windows 10 Pro Endpoints: 0')
    args.endpoints_count = 0 
else:
    print("[+] Number of Windows 10 Pro endpoints desired: ", args.endpoints_count)
    logging.info('[+] Number of Windows 10 Pro endpoints desired: %s', args.endpoints_count)

# parse the resource group name if specified
default_rg_name = "PurpleCloud"
if not args.resource_group:
    print("[+] Using default Resource Group Name: ", default_rg_name)
    logging.info('[+] Using default Resource Group Name: %s', default_rg_name)
else:
    default_rg_name = args.resource_group
    print("[+] Using Resource Group Name: ", default_rg_name)
    logging.info('[+] Using Resource Group: %s', default_rg_name)

# parse the Azure location if specified
supported_azure_locations = ['westus', 'westus2', 'eastus', 'centralus', 'centraluseuap', 'southcentralus' , 'northcentralus', 'westcentralus', 'eastus2', 'eastus2euap', 'brazilsouth', 'brazilus', 'northeurope', 'westeurope', 'eastasia', 'southeastasia', 'japanwest', 'japaneast', 'koreacentral', 'koreasouth', 'southindia', 'westindia', 'centralindia', 'australiaeast', 'australiasoutheast', 'canadacentral', 'canadaeast', 'uksouth', 'ukwest', 'francecentral', 'francesouth', 'australiacentral', 'australiacentral2', 'uaecentral', 'uaenorth', 'southafricanorth', 'southafricawest', 'switzerlandnorth', 'switzerlandwest', 'germanynorth', 'germanywestcentral', 'norwayeast', 'norwaywest', 'brazilsoutheast', 'westus3', 'swedencentral', 'swedensouth'
]
default_location = "eastus"
if not args.location:
    print("[+] Using default location: ", default_location)
    logging.info('[+] Using default location: %s', default_location)
else:
    default_location = args.location
    if default_location in supported_azure_locations:
        # this is a supported Azure location
        print("[+] Using Azure location: ", default_location)
        logging.info('[+] Using Azure location: %s', default_location)
    else:
        print("[-] This is not a supported azure location: ",default_location)
        print("[-] Check the supported_azure_locations if you need to add a new official Azure location")
        exit()

# The default AD Users
# The groups field is the AD Group that will be automatically created
# An OU will be auto-created based on the AD Group name, and the Group will have OU path set to it 
default_ad_users = [
    {
        "name":"Lars Borgerson",
        "ou": "CN=users,DC=rtc,DC=local",
        "password": get_password(),
        "domain_admin":"",
        "groups":"IT"
    },
    {
        "name":"Olivia Odinsdottir",
        "ou": "CN=users,DC=rtc,DC=local",
        "password": get_password(),
        "domain_admin":"True",
        "groups":"IT"
    },
    {
        "name":"Liem Anderson",
        "ou": "CN=users,DC=rtc,DC=local",
        "password": get_password(),
        "domain_admin":"",
        "groups":"IT"
    },
    {
        "name":"John Nilsson",
        "ou": "CN=users,DC=rtc,DC=local",
        "password": get_password(),
        "domain_admin":"",
        "groups":"IT"
    },
    {
        "name":"Jason Lindqvist",
        "ou": "CN=users,DC=rtc,DC=local",
        "password": get_password(),
        "domain_admin":"True",
        "groups":"IT"
    },
]

# Parse the AD users to get one Domain Admin for bootstrapping systems
if args.dc_enable:
    da_count = 0
    for user in default_ad_users:

        # Set up a dictionary to store name and password
        user_dict = {'name': '', 'pass':''}
        user_dict['name'] = user['name'] 

        if user['domain_admin'].lower() == 'true':
            da_count+=1
            names = user['name'].split()
            default_winrm_username = names[0].lower() + names[1].lower()
            default_winrm_password = user['password']

            # set password to default domain admin password
            user_dict['pass'] = default_da_password
        else:
            # set password to default ad user password
            user_dict['pass'] = default_aduser_password

        # Append to all_ad_users
        all_ad_users.append(user_dict)

    if da_count >= 1:
        pass
    else:
        print("[-] At least one Domain Admin in default_ad_users must be enabled")
        exit()

# Install sysmon on endpoints, true by default
install_sysmon_enabled = True 
sysmon_endpoint_config = ""
if install_sysmon_enabled == True:
    sysmon_endpoint_config = "true"
else:
    sysmon_endpoint_config = "false"

# Install art, false by default
install_art = False

# Names of the terraform files
tmain_file = "main_sentinel.tf"
tproviders_file = "providers.tf"
tmidentity_file = "midentity.tf"
tnet_file = "network_sentinel.tf"
tnsg_file = "nsg_sentinel.tf"
tdc_file = "dc_sentinel.tf"
tsentinel_file = "sentinel.tf"
tsysmon_file = "sysmon_sentinel.tf"

### NETWORK CONFIGURATION
### ADD ADDITIONAL NETWORKS BELOW
### Configuration for VNets
config_vnets = [
    {
        "name":"vnet1",
        "prefix":"10.100.0.0/16",
        "type":"default"
    }
]
### Configuration for Subnets
config_subnets = [
    { 
        "name":"ad_subnet",
        "prefix":"10.100.10.0/24",
        "type":"ad_vlan"
    },
    {
        "name":"user_subnet",
        "prefix":"10.100.20.0/24",
        "type":"user_vlan"
    },
    {
        "name":"security_subnet",
        "prefix":"10.100.30.0/24",
        "type":"sec_vlan"
    },
    {
        "name":"attack_subnet",
        "prefix":"10.100.40.0/24",
        "type":""
    }
]

### WINDOWS 10 CONFIGURATION / CONFIGURATION FOR WINDOWS 10 PRO ENDPOINTS
### The Default Configuration for all of the Windows 10 Endpoints
config_win10_endpoint = { 
    "hostname_base":"win10",
    "join_domain":"false",
    "auto_logon_domain_user":"false",
    "install_sysmon":sysmon_endpoint_config,
    "install_art":"true",
}

## Check if office 365 data connector is enabled
if args.odc_enable:
    print("[+] Office 365 data connector will be enabled for Sentinel")

## Check if Azure AD data connector is enabled
if args.adc_enable:
    print("[+] Azure AD data connector will be enabled for Sentinel")


## Check if domain_join argument is enabled
## If it is, set the configuration above
if args.domain_join:
    print("[+] Domain Join is set to true")
    logging.info('[+] Domain Join is set to true')
    config_win10_endpoint['join_domain'] = "true"

## Check if auto_logon argument is enabled
## If it is, set the configuration above
if args.auto_logon:
    print("[+] Auto Logon is set to true")
    logging.info('[+] Auto Logon is set to true')
    config_win10_endpoint['auto_logon_domain_user'] = "true"

## Check the configuration above
## Can only join the domain or auto logon domain users if dc enable
if config_win10_endpoint['join_domain'].lower() == 'true' or config_win10_endpoint['auto_logon_domain_user'].lower == 'true':
    if args.dc_enable:
        pass
    else:
        print("[-] The Domain controller option must be enabled for Domain Join or Auto Logon Domain Users")
        print("[-] Current setting for join_domain: ", config_win10_endpoint['join_domain'])
        print("[-] Current setting for auto_logon_domain_user: ", config_win10_endpoint['auto_logon_domain_user'])
        exit()

### Windows 10 Pro endpoint count
### How many Windows 10 to build in this range?
win10_count = int(args.endpoints_count) 

# check to make win10sure config__endpoint is correct for true or false values
if config_win10_endpoint['join_domain'].lower() != 'false' and config_win10_endpoint['join_domain'].lower() != 'true':
    print("[-] Setting join_domain must be true or false")
    exit()
if config_win10_endpoint['auto_logon_domain_user'].lower() != 'false' and config_win10_endpoint['auto_logon_domain_user'].lower() != 'true':
    print("[-] Setting auto_logon_domain_user must be true or false")
    exit()
if config_win10_endpoint['install_sysmon'].lower() != 'false' and config_win10_endpoint['install_sysmon'].lower() != 'true':
    print("[-] Setting install_sysmon must be true or false")
    exit()
if config_win10_endpoint['install_art'].lower() != 'false' and config_win10_endpoint['install_art'].lower() != 'true':
    print("[-] Setting install_art must be true or false")
    exit()

### Do some inspection of the vnets to make sure no duplicates
default_vnet_name = ""
default_vnet_prefix = ""

vnet_names = []
vnet_prefixes = []
vnet_default_count = 0
for vnet in config_vnets:

    # network name
    net_name = vnet['name']
    vnet_names.append(net_name)

    # prefix
    prefix = vnet['prefix']
    vnet_prefixes.append(prefix)

    # type
    type = vnet['type']

    if ( type == "default" ):
        default_vnet_name = net_name
        default_vnet_prefix = prefix
        vnet_default_count+=1

def check_cidr_subnet(subnet_cidr_str):
    # Check the cidr or subnet to make sure it looks correct
    elements = subnet_cidr_str.split('.')
    if len(elements) != 4:
        print("[-] The subnet or CIDR is not in correct format:",subnet_cidr_str)
        print("[-] Correct examples include: 10.100.30.0/24")
        print("[-] Correct examples include: 10.100.0.0/16")
        return False

    octet1 = int(elements[0])
    if ((octet1 >= 0) and (octet1 <= 255)):
        pass
    else:
        print("[-] Error parsing the subnet or CIDR ~ not in correct format:", subnet_cidr_str)
        print("[-] Problem: ",octet1)
        return False

    octet2 = int(elements[1])
    if ((octet2 >= 0) and (octet2 <= 255)):
        pass
    else:
        print("[-] Error parsing the subnet or CIDR ~ not in correct format:", subnet_cidr_str)
        print("[-] Problem: ",octet2)
        return False

    octet3 = int(elements[2])
    if ((octet3 >= 0) and (octet3 <= 255)):
        pass
    else:
        print("[-] Error parsing the subnet or CIDR ~ not in correct format:", subnet_cidr_str)
        print("[-] Problem: ",octet3)
        return False

    last = elements[3]
    split_last = last.split('/')
    if len(split_last) != 2:
        print("[-] Error parsing the subnet or CIDR ~ not in correct format:", subnet_cidr_str)
        return False
    octet4 = int(split_last[0])
    if ((octet4 >= 0) and (octet4 <= 255)):
        pass
    else:
        print("[-] Error parsing the subnet or CIDR ~ not in correct format:", subnet_cidr_str)
        print("[-] Problem: ",octet4)
        return False

    octet5 = int(split_last[1])
    if ((octet5 >= 0) and (octet5 <= 32)):
        pass
    else:
        print("[-] Error parsing the subnet or CIDR ~ not in correct format:", subnet_cidr_str)
        print("[-] Problem: ",octet5)
        return False

    return True


# Check to make sure only one default vnet
if vnet_default_count != 1:
    print("[-] Only one default vnet type allowed")
    print('[-] Ensure that config_vnets has only one entry for "type":"default"')
    exit()

## Check for duplicate vnet names in config_vnets
if len(vnet_names) == len(set(vnet_names)):
    # No duplicate vnet names found
    pass
else:
    print("[-] Duplicate vnet names found")
    print("[-] Please ensure that each vnet name is unique in config_vnets")
    exit()

## Check for duplicate vnet prefixes in config_vnets
if len(vnet_prefixes) == len(set(vnet_prefixes)):
    # No duplicate vnet names found
    pass
else:
    print("[-] Duplicate vnet prefixes found")
    print("[-] Please ensure that each vnet prefix is unique in config_vnets")
    exit()

for prefix in vnet_prefixes:
    retval = check_cidr_subnet(prefix)
    if retval:
        pass
    else:
        print("[-] Invalid CIDR or subnet, exit")
        print("[-] Correct examples include: 10.100.30.0/24")
        print("[-] Correct examples include: 10.100.0.0/16")
        exit()

### Do some inspection of the subnets to make sure no duplicates
subnet_names = []
subnet_prefixes = []
user_vlan_count = 0
ad_vlan_count = 0
security_vlan_count = 0
security_subnet_prefix = ""
security_subnet_name = ""
ad_subnet_name = ""
ad_subnet_prefix = ""
helk_ip = ""
user_subnet_name = ""
user_subnet_prefix = ""
for subnet in config_subnets:

    # network name
    net_name = subnet['name']
    subnet_names.append(net_name)

    # prefix
    prefix = subnet['prefix']
    subnet_prefixes.append(prefix)

    # type
    type = subnet['type']
    if type == 'user_vlan':
        #DEBUGprint("[+] Found user vlan name:", net_name)
        ## assign the user vlan name variable for later users
        user_subnet_name = net_name 
        user_subnet_prefix = prefix 
        user_vlan_count+=1
    elif (type == 'ad_vlan'):
        #DEBUGprint("[+] Found ad vlan name:", net_name)
        ad_subnet_prefix = prefix 
        ad_subnet_name = net_name 
        ad_vlan_count+=1
    elif (type == 'security_vlan'):
        security_subnet_prefix = prefix 
        security_subnet_name = net_name 
        security_vlan_count+=1
    else:
        pass

## Check for duplicate subnet names in config_subnets
if len(subnet_names) == len(set(subnet_names)):
    # No duplicate subnet names found
    pass
else:
    print("[-] Duplicate subnet names found")
    print("[-] Please ensure that each subnet name is unique in config_subnets")
    exit()

## Check for duplicate subnet prefixes in config_subnets
if len(subnet_prefixes) == len(set(subnet_prefixes)):
    # No duplicate subnet names found
    pass
else:
    print("[-] Duplicate subnet prefixes found")
    print("[-] Please ensure that each subnet prefix is unique in config_subnets")
    exit()

# Check to make sure more than one user_vlan is not enabled
if user_vlan_count > 1:
    print("[-] user vlans greater than 1.  Please specify one only one user vlan")

# Check to make sure more than one ad_vlan is not enabled
if ad_vlan_count > 1:
    print("[-] ad vlans greater than 1.  Please specify one only one ad vlan")

for prefix in subnet_prefixes:
    retval = check_cidr_subnet(prefix)
    if retval:
        pass
    else:
        print("[-] Invalid CIDR or subnet, exit")
        print("[-] Correct examples include: 10.100.30.0/24")
        print("[-] Correct examples include: 10.100.0.0/16")
        exit()

## Get dc_ip if dc is enabled
if args.dc_enable:
    if ad_vlan_count == 1:
        # This is the last octet of the helk_ip
        last_octet = "4"
        elements = ad_subnet_prefix.split('.')
        dc_ip = elements[0] + "." + elements[1] + "." + elements[2] + "." + last_octet
    else:
        print("[-] DC is enabled without a subnet assignment")
        print("[-] Set a type of ad_vlan to one of the subnets")
        exit()

###
# Beginning of templates
###

# user_subnet start IP address
# If the user subnet is 10.100.30.0/24: 
# start the workstations at 10.100.30.x where x is first_ip_user_subnet variable 
first_ip_user_subnet = "10"

def get_endpoint_template():
    template = '''
variable "ENDPOINT_IP_VAR_NAME" {
  default = "ENDPOINT_IP_DEFAULT"
}

variable "ADMIN_USERNAME_VAR_NAME" {
  default = "ADMIN_USERNAME_DEFAULT"
}

variable "ADMIN_PASSWORD_VAR_NAME" {
  default = "ADMIN_PASSWORD_DEFAULT"
}

variable "ENDPOINT_HOSTNAME_VAR_NAME" {
  default = "ENDPOINT_HOSTNAME_DEFAULT"
}

resource "azurerm_public_ip" "AZURERM_PUBLIC_IP_VAR_NAME" {
  name                = "${var.ENDPOINT_HOSTNAME_VAR_NAME}-public-ip-${random_string.suffix.id}"
  location            = var.location
  resource_group_name = "${var.resource_group_name}-${random_string.suffix.id}"
  allocation_method   = "Static"
}

resource "azurerm_network_interface" "AZURERM_NETWORK_INTERFACE_VAR_NAME" {
  name                = "${var.ENDPOINT_HOSTNAME_VAR_NAME}-int-nic-${random_string.suffix.id}"
  location            = var.location
  resource_group_name = "${var.resource_group_name}-${random_string.suffix.id}"
  internal_dns_name_label = "${var.ENDPOINT_HOSTNAME_VAR_NAME}-${random_string.suffix.id}"

  ip_configuration {
    name                          = "primary"
    subnet_id                     = azurerm_subnet.user_subnet.id
    private_ip_address_allocation = "Static"
    private_ip_address            = var.ENDPOINT_IP_VAR_NAME
    public_ip_address_id          = azurerm_public_ip.AZURERM_PUBLIC_IP_VAR_NAME.id
  }
}

resource "azurerm_virtual_machine" "AZURERM_WINDOWS_VIRTUAL_MACHINE_VAR_NAME" {
  name                          = "${var.ENDPOINT_HOSTNAME_VAR_NAME}-${random_string.suffix.id}"
  resource_group_name           = "${var.resource_group_name}-${random_string.suffix.id}"
  location                      = var.location
  vm_size                       = "Standard_D2as_v4"
  delete_os_disk_on_termination = true

  network_interface_ids = [
    azurerm_network_interface.AZURERM_NETWORK_INTERFACE_VAR_NAME.id,
  ]

  storage_image_reference {
    publisher = "MicrosoftWindowsDesktop"
    offer     = "Windows-10"
    sku       = "win10-22h2-pro-g2"
    version   = "latest"
  }

  storage_os_disk {
    name              = "${var.ENDPOINT_HOSTNAME_VAR_NAME}-osdisk"
    caching           = "ReadWrite"
    managed_disk_type = "Standard_LRS"
    create_option     = "FromImage"
  }

  os_profile {
    computer_name  = var.ENDPOINT_HOSTNAME_VAR_NAME
    admin_username = var.ADMIN_USERNAME_VAR_NAME
    admin_password = var.ADMIN_PASSWORD_VAR_NAME
  }
}
'''
    return template

def get_midentity_template():
    template = '''

# Create the User Assigned Managed Identity
resource "azurerm_user_assigned_identity" "uai" {
  resource_group_name = azurerm_resource_group.network.name
  location            = var.location
  name                = var.identity_name
}

variable "identity_name" {
  default = "uaidentity"
}

variable "identity_type" {
  default = "SystemAssigned, UserAssigned"
}

# add 'Owner' role scoped to subscription for user-assigned managed identity
resource "azurerm_role_assignment" "owner_uai" {
  scope                = data.azurerm_subscription.mi.id
  role_definition_name = "Owner"
  principal_id         = azurerm_user_assigned_identity.uai.principal_id
}

# add 'Virtual Machine Contributor' role scoped to subscription for user-assigned managed identity
resource "azurerm_role_assignment" "vm_contributor_uai" {
  scope                = data.azurerm_subscription.mi.id
  role_definition_name = "Virtual Machine Contributor"
  principal_id         = azurerm_user_assigned_identity.uai.principal_id
}

# add 'Key Vault Reader' role scoped to subscription for user-assigned managed identity
resource "azurerm_role_assignment" "key_vault_reader_uai" {
  scope                = data.azurerm_subscription.mi.id
  role_definition_name = "Key Vault Reader"
  principal_id         = azurerm_user_assigned_identity.uai.principal_id
}

data "azurerm_subscription" "mi" {
}

output "managed_identity_details" {
  value = <<EOS
-------------------------
Managed Identity Details
-------------------------
Subscription ID:   ${split("/", data.azurerm_subscription.mi.id)[2]}
Subscription Name: ${data.azurerm_subscription.mi.display_name}
Resource Group:    ${azurerm_resource_group.network.name}

User-Assigned Identity:
-------------------------
Name:        ${azurerm_user_assigned_identity.uai.name}
Client ID'''
