import json
import argparse
import yaml
import requests
from datetime import tzinfo, timedelta, datetime
import datetime

commandline = argparse.ArgumentParser(prog='PROG')
commandline.add_argument('--SellerURL')
commandline.add_argument('--SellerName')
commandline.add_argument('--password')
args = commandline.parse_args()

SellerprofileIP = 'http://'+str(args.SellerURL)+'/api/profile/'
SellermarketIP = 'http://'+str(args.SellerURL)+'/api/marketplace/'
SellermailerIP = 'http://'+str(args.SellerURL)+'/api/mailer/'

def seconds(t1, t2):
    h1, m1, s1 = t1.hour, t1.minute, t1.second
    h2, m2, s2 = t2.hour, t2.minute, t2.second
    t1_secs = s1 + 60 * (m1 + 60*h1)
    t2_secs = s2 + 60 * (m2 + 60*h2)
    aa = str(datetime.timedelta(seconds=( t2_secs - t1_secs)))
    return( aa)

def loginSeller():
    url = SellerprofileIP+"users/login"
    payload = {"userName":str(args.SellerName), "password":str(args.password)}
    headers = {"Content-Type":"application/json"}
    req = requests.post(url, headers=headers, data=json.dumps(payload))
    response = req.json()
    return response

def yamldata(filename):
    with open(filename, 'r') as file:
        data = yaml.load(file)
    return data

def imagefile(file):
    headers = {'Content-Type' : 'image/jpeg'}
    url = SellermailerIP+'/file/image'
    files = {'myfile': (file, open(file, 'rb'), 'image/jpg')}
    res = requests.post(url, files=files)
    return res.json()["file"][0]["_id"]

def createlisting(SellerToken, SellerAuth):
    data = yamldata("Listingsinput.yaml")
    inputs = yamldata("listing.yaml")
    datalisting = data["createlisting"]
    datalisting["userId"] = inputs["createlisting"]["userId"]
    datalisting["accountType"] = inputs["createlisting"]["accountType"]
    datalisting["listName"] = inputs["createlisting"]["listName"]

    d = datetime.datetime.today()

    time = seconds( datetime.datetime.strptime( "05:30:00", '%H:%M:%S').time(),datetime.datetime.strptime( str(d.hour)+":"+str(d.minute)+":"+str(d.second), '%H:%M:%S').time())
    publishDate = str(inputs["createlisting"]["publishDate"])+" "+str(time)
    publishDate = datetime.datetime.strptime(str(publishDate), '%Y-%m-%d %H:%M:%S')

    datalisting["publishDate"] = publishDate.isoformat()
    expiryDate = str(inputs["createlisting"]["expiryDate"])+" 10:05:00"
    expiryDate = datetime.datetime.strptime(expiryDate, '%Y-%m-%d %H:%M:%S')
    datalisting["expiryDate"] = expiryDate.isoformat()

    datalisting["templateName"] = inputs["createlisting"]["templateName"]

    headers = {"Content-Type":"application/json", "token":SellerToken}

    countryres = requests.get(SellermailerIP+"geo/countries", headers={"Content-Type":"application/json"})
    for i in range(len(inputs["createlisting"]["regionName"])):
        for j in range(len(countryres.json()["data"])):
            regionname = inputs["createlisting"]["regionName"][i]
            if regionname.title() == countryres.json()["data"][j]["countryName"]:
                countrydetails = {"regionId":countryres.json()["data"][j]["countryId"], "regionName":countryres.json()["data"][j]["countryName"]}
                datalisting["eligibleRegions"].append(countrydetails)

    req = requests.post(SellermarketIP+"listings", headers=headers, data=json.dumps(datalisting))
    getlistId = requests.get(SellermarketIP+"listings/lists?listRef="+req.json()["ref"], headers=headers)

    #return getlistId.json()["listId"],req.json()["ref"]
    return getlistId.json(),req.json()["ref"]

def setbrand(datalisting, Brand):
    if Brand=='Dell' or Brand=='dell':
        datalisting["caliber"] = '10mm'
    elif Brand=='HP' or Brand=='hp':
        datalisting["caliber"] = '380m'
    elif Brand=='Mac' or Brand=='mac':
        datalisting["caliber"] = '38spc'
    elif Brand=='Sony' or Brand=='sony':
        datalisting["caliber"] = '9mm'
    elif Brand=='Samsung' or Brand=='samsung':
        datalisting["caliber"] = '49colt'

def setprinterbrand(dataproduct, Brand):
    if Brand=='Dell' or Brand=='dell':
        dataproduct["caliber"] = 'propellant'
    elif Brand=='Canon' or Brand=='canon':
        dataproduct["caliber"] = 'ninemm'
    elif Brand=='HP' or Brand=='hp':
        dataproduct["caliber"] = 'sevenpoint'
    elif Brand=='Epson' or Brand=='epson':
        dataproduct["caliber"] = 'cal'
    elif Brand=='Samsung' or Brand=='samsung':
        dataproduct["caliber"] = 'threeNot'

def productlisting(token, listingref):
    data = yamldata("Listingsinput.yaml")
    inputs = yamldata("listing.yaml")

    dataproduct = data["productlisting"]

    dataproduct["productName"] = inputs["productlisting"]["productName"]
    dataproduct["productDescription"] = inputs["productlisting"]["productDescription"]

    image = inputs["productlisting"]["productImage"]
    dataproduct["productImage"][0]["imgSrcUrl"] = imagefile(image)

    dataproduct["manufacturingDetails"]["productionYear"] = inputs["productlisting"]["manufacturingDetails"]["productionYear"]
    dataproduct["packagingDetails"] = inputs["productlisting"]["packagingDetails"]
    dataproduct["pricingDetails"] = inputs["productlisting"]["pricingDetails"]

    countryres = requests.get(SellermailerIP+"geo/countries", headers={"Content-Type":"application/json"})

    for j in range(len(countryres.json()["data"])):
        regionname = inputs["productlisting"]["manufacturingDetails"]["productMfgCountry"]
        if regionname.title() == countryres.json()["data"][j]["countryName"]:
            dataproduct["manufacturingDetails"]["productMfgCountry"] = countryres.json()["data"][j]["countryId"]

    if inputs["productlisting"]["product"]=='Computer' or inputs["productlisting"]["product"]=='computer':
        dataproduct["productType"]["value"] = 1
        if inputs["productlisting"]["Type"]=='Desktop' or inputs["productlisting"]["Type"]=='Desktop':
            dataproduct["productType"]["ammunitionType"]["value"] = 1
            setbrand(dataproduct["productType"]["ammunitionType"], inputs["productlisting"]["Brand"])
        elif inputs["productlisting"]["Type"]=='Laptop' or inputs["productlisting"]["Type"]=='laptop':
            dataproduct["productType"]["ammunitionType"]["value"] = 2
            setbrand(dataproduct["productType"]["ammunitionType"], inputs["productlisting"]["Brand"])
        elif inputs["productlisting"]["Type"]=='Notebook' or inputs["productlisting"]["Type"]=='notebook':
            dataproduct["productType"]["ammunitionType"]["value"] = 3
            setbrand(dataproduct["productType"]["ammunitionType"], inputs["productlisting"]["Brand"])
        elif inputs["productlisting"]["Type"]=='2 In 1 Laptop' or inputs["productlisting"]["Type"]=='2 in 1 laptop':
            dataproduct["productType"]["ammunitionType"]["value"] = 4
            setbrand(dataproduct["productType"]["ammunitionType"], inputs["productlisting"]["Brand"])
    else:
        dataproduct["productType"]["value"] = 2
        if inputs["productlisting"]["Type"]=='Ink-Jet' or inputs["productlisting"]["Type"]=='ink-jet':
            dataproduct["productType"]["ammunitionType"]["value"] = 1
            setprinterbrand(dataproduct["productType"]["ammunitionType"], inputs["productlisting"]["Brand"])
        elif inputs["productlisting"]["Type"]=='Laser' or inputs["productlisting"]["Type"]=='laser':
            dataproduct["productType"]["ammunitionType"]["value"] = 2
            setprinterbrand(dataproduct["productType"]["ammunitionType"], inputs["productlisting"]["Brand"])
        elif inputs["productlisting"]["Type"]=='3D' or inputs["productlisting"]["Type"]=='3d':
            dataproduct["productType"]["ammunitionType"]["value"] = 3
            setprinterbrand(dataproduct["productType"]["ammunitionType"], inputs["productlisting"]["Brand"])
        elif inputs["productlisting"]["Type"]=='Dot-Matrix' or inputs["productlisting"]["Type"]=='dot-matrix':
            dataproduct["productType"]["ammunitionType"]["value"] = 4
            setprinterbrand(dataproduct["productType"]["ammunitionType"], inputs["productlisting"]["Brand"])

    headers = {"Content-Type":"application/json", "token":token}
    dataproduct["listId"] = listingref
    req = requests.post(SellermarketIP+"listings/products", headers=headers, data=json.dumps(dataproduct))
    return req.json()

def updatelisting(token, listref):
    inputs = yamldata("listing.yaml")
    listName = inputs["createlisting"]["listName"]
    payload = {"ref":listref,"info":{"listName": listName}}
    headers = {"Content-Type":"application/json", "token":token}

    res = requests.patch(SellermarketIP+"listings", headers=headers, data=json.dumps(payload))
    publish = {"ref": listref}
    requests.patch(SellermarketIP+"listings/publish", headers=headers, data=json.dumps(publish))

#/listings/publish patch

def sukudemo():
    loginSellerres = loginSeller()
    listingres = createlisting(loginSellerres['data']['token'], loginSellerres['data']['authId'])
    productres = productlisting(loginSellerres['data']['token'], listingres[1])
    updatelisting(loginSellerres['data']['token'], listingres[1])

sukudemo()
