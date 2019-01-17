import json
import argparse
import yaml
import requests

commandline = argparse.ArgumentParser(prog='PROG')
commandline.add_argument('--buyerURL')
commandline.add_argument('--buyerName')
commandline.add_argument('--password')
args = commandline.parse_args()

buyerprofileIP = 'http://'+str(args.buyerURL)+'/api/profile/'
buyermarketIp = 'http://'+str(args.buyerURL)+'/api/marketplace/'
buyermailerIp = 'http://'+str(args.buyerURL)+'/api/mailer/'

def loginbuyer():
    url = buyerprofileIP+"users/login"
    payload = {"userName":str(args.buyerName), "password":str(args.password)}
    headers = {"Content-Type":"application/json"}

    req = requests.post(url, headers=headers, data=json.dumps(payload))
    response = req.json()
    return response

def yamldata(filename):
	with open(filename, 'r') as file:
		data = yaml.load(file)
	return data

def setbuybrand(datalisting, Brand):
    if Brand=='Dell':
        datalisting["caliber"] = '10mm'
    elif Brand=='HP':
        datalisting["componentType"]["caliber"] = 'Shotgun'
    elif Brand=='Mac':
        datalisting["componentType"]["caliber"] = '.380'
    elif Brand=='Sony':
        datalisting["componentType"]["caliber"] = '9mm'
    elif Brand=='Samsung':
        datalisting["componentType"]["caliber"] = '45Colt'

def setprinterbrandbuy(dataproduct, Brand):
    if Brand=='Dell':
        dataproduct["caliber"] = '5.56'
    elif Brand=='Canon':
        dataproduct["caliber"] = '9mm'
    elif Brand=='HP':
        dataproduct["caliber"] = '7.62/39'
    elif Brand=='Epson':
        dataproduct["caliber"] = '50cal'
    elif Brand=='Samsung':
        dataproduct["caliber"] = '308'

def createinterest(buyerToken, buyerAuth):
    data = yamldata("interestinputs.yaml")
    inputs = yamldata("interest.yaml")

    datainterest = data["createinterest"]

    datainterest["interestName"] = inputs["createinterest"]["interestName"]
    datainterest["templateName"] = inputs["createinterest"]["templateName"]
    datainterest["userId"] = inputs["createinterest"]["userId"]
    datainterest["accountType"] = inputs["createinterest"]["accountType"]
    datainterest["publishDate"] = inputs["createinterest"]["publishDate"]
    datainterest["expiryDate"] = inputs["createinterest"]["expiryDate"]
    datainterest["priceRangeFrom"] = inputs["createinterest"]["priceRangeFrom"]
    datainterest["priceRangeTo"] = inputs["createinterest"]["priceRangeTo"]
    datainterest["quantityRangeFrom"] = inputs["createinterest"]["quantityRangeFrom"]
    datainterest["quantityRangeTo"] = inputs["createinterest"]["quantityRangeTo"]

    headers = {"Content-Type":"application/json", "token":buyerToken}

    countryres = requests.get(buyermailerIp+"geo/countries", headers={"Content-Type":"application/json"})
    for i in range(len(inputs["createinterest"]["regionName"])):
        for j in range(len(countryres.json()["data"])):
            if inputs["createinterest"]["regionName"][i] == countryres.json()["data"][j]["countryName"]:
                countrydetails = {"regionId":countryres.json()["data"][j]["countryId"], "regionName":countryres.json()["data"][j]["countryName"]}
                datainterest["eligibleRegions"].append(countrydetails)

    if inputs["createinterest"]["product"]=='Computer':
        datainterest["preferenceType"]["value"] = 1
        if inputs["createinterest"]["Type"]=='Desktop':
            datainterest["preferenceType"]["ammunitionType"]["value"] = 1
            setbuybrand(datainterest["preferenceType"], inputs["createinterest"]["Brand"])
        elif inputs["createinterest"]["Type"]=='Laptop':
            datainterest["preferenceType"]["ammunitionType"]["value"] = 2
            setbuybrand(datainterest["preferenceType"], inputs["createinterest"]["Brand"])
        elif inputs["createinterest"]["Type"]=='Notebook':
            datainterest["preferenceType"]["ammunitionType"]["value"] = 3
            setbuybrand(datainterest["preferenceType"], inputs["createinterest"]["Brand"])
        elif inputs["createinterest"]["Type"]=='2 In 1 Laptop':
            datainterest["preferenceType"]["ammunitionType"]["value"] = 4
            setbuybrand(datainterest["preferenceType"], inputs["createinterest"]["Brand"])
    else:
        datainterest["preferenceType"]["value"] = 2
        if inputs["createinterest"]["Type"]=='Ink-Jet':
            datainterest["preferenceType"]["ammunitionType"]["value"] = 1
            setprinterbrandbuy(datainterest["preferenceType"], inputs["createinterest"]["Brand"])
        elif inputs["createinterest"]["Type"]=='Laser':
            datainterest["preferenceType"]["ammunitionType"]["value"] = 2
            setprinterbrandbuy(datainterest["preferenceType"], inputs["createinterest"]["Brand"])
        elif inputs["createinterest"]["Type"]=='3D':
            datainterest["preferenceType"]["ammunitionType"]["value"] = 3
            setprinterbrandbuy(datainterest["preferenceType"], inputs["createinterest"]["Brand"])
        elif inputs["createinterest"]["Type"]=='Dot-Matrix':
            datainterest["preferenceType"]["ammunitionType"]["value"] = 4
            setprinterbrandbuy(datainterest["preferenceType"], inputs["createinterest"]["Brand"])

    req = requests.post(buyermarketIp+"interests", headers=headers, data=json.dumps(datainterest))

    getinterestId = requests.get(buyermarketIp+"interest/interest?interestRef="+req.json()["ref"], headers=headers)
    return getinterestId.json()

def sukudemo():
    loginbuyerres = loginbuyer()
    interestres = createinterest(loginbuyerres['data']['token'], loginbuyerres['data']['authId'])

sukudemo()