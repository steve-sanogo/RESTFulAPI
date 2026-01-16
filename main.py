from flask import Flask, request, jsonify
from pymongo import MongoClient
from _datetime import datetime  # allow us to get the time and date when a document is modify
import os
from dotenv import load_dotenv

load_dotenv()
mongo_uri = os.getenv("MONGO_URI")

if not mongo_uri:
    raise ValueError("La variable MONGO_URI n'est pas définie dans le fichier .env")

cluster = MongoClient(mongo_uri)

db = cluster['world']  # switch to venture db
collection = db['countries']
update_collection = db['update']

app = Flask(__name__)

regions_list = collection.distinct("region")
countries_list = collection.distinct("name")
subRegion_list = collection.distinct("subregion")
field_list = list()  # contain all the field on the collection.

# get all the field on the collection.
for key in collection.find_one().keys():
    field_list.append(key)


# regions_list, countries_list, field_list will be use later to verify user queries related to a field, a region or
# a country in the dataset


@app.route('/infos')
def index():
    return "RESTfull Project with Flask v1.1"


# This URI allows to users to have some information about a particular country.
@app.route('/country/<region>/<name>', methods=['GET'])
def country(region, name):
    if region in regions_list:  # verify the region enter by User.
        if name in countries_list:  # verify the country name enter by User
            result = collection.find_one({"name": name, "region": region},
                                         {'name': 1, 'capital': 1, 'population': 1, 'region': 1, 'subregion': 1,
                                          "_id": 0})
        else:
            result = {"Ok": 0, "msg": "The country doesn't exists, please check it."}
    else:
        result = {"Ok": 0, "msg": "The continent name doesn't exists.It should be among : " + str(regions_list[1:])}

    return jsonify(result)


# This URI allows to users to have a specific information about a country.
@app.route('/country/<region>/<name>/<field>', methods=['GET'])
def countryF(region, name, field):
    if region in regions_list:  # verify the region enter by User.
        if name in countries_list:  # verify the country name enter by User
            if field in field_list:  # verify "field" enter by User
                result = collection.find_one({"name": name, "region": region},
                                             {'name': 1, field: 1, "_id": 0})
            else:
                result = {"Ok": 0, "msg": "The field doesn't exists, please choice within : " + str(field_list)}
        else:
            result = {"Ok": 0, "msg": "The country doesn't exists, please check it"}
    else:
        result = {"Ok": 0, "msg": "The continent name doesn't exists.It should be among : " + str(regions_list[1:])}
    return jsonify(result)


# Find All the countries on a specific world region, specifying the field.
@app.route('/countries/<region>/<field>', methods=['GET'])
def RegionCountries(region, field):
    if region in regions_list:  # verify "region" enter by the user.
        if field in field_list:  # verify "field" enter by the user.
            result = collection.find({"region": region}, {'name': 1, field: 1, "_id": 0})
            outPut = []  # list that will contain the different countries returned by the request
            for element in result:
                outPut.append({'name': element['name'], field: element[field]})
        else:
            outPut = {"Ok": 0, "msg": "The field doesn't exists, please check it"}
    else:
        outPut = {"Ok": 0, "msg": "The continent name doesn't exists.It should be among : " + str(regions_list[1:])}

    return jsonify({"result": outPut})


#
@app.route('/countries/<region>/<subregion>/<field>', methods=['GET'])
def countries(region, subregion, field):
    if region in regions_list:  # verify "region" enter by the user.
        if field in field_list:  # verify "field" enter by the user.
            if subregion in subRegion_list:
                result = collection.find({"region": region, "subregion": subregion}, {'name': 1, field: 1, "_id": 0})
                outPut = []  # list that will contain the different countries returned by the request
                for element in result:
                    outPut.append({'name': element['name'], field: element[field]})
            else:
                outPut = {"Ok": 0, "msg": "The subregion  doesn't exists.It should be among : " + str(subRegion_list[1:])}
        else:
            outPut = {"Ok": 0, "msg":  "The field doesn't exists, please check it"}
    else:
        outPut = {"Ok": 0, "msg":  "The continent name doesn't exists.It should be among : " + str(regions_list[1:])}

    return jsonify({"result": outPut})


# This URI allows to users to get a particular region(continent) field count or average. It uses like this:
# www.world.com/continent/<region>/<operation>/<field>, operation can be "count" or "average"
@app.route('/continent/<region>/<subregion>/<operation>/<field>', methods=['GET'])
def continentSubRegionOperation(region, subregion, operation, field):
    countable_field = ['population', 'area', 'gini', 'countries']
    allowed_operation = ['count', 'average']
    if region in regions_list:  # verify "region" value enter by the user.
        if field in countable_field:  # verify "field" value enter by the user.
            if subregion in subRegion_list:  # verify "subregion" value enter by the user.
                if operation in allowed_operation:  # verify "operation" value enter by the user.
                    operation = "$sum" if operation == "count" else "$avg"
                    if field == countable_field[-1]:  # field = "countries"
                        pipeline = [{"$match": {"subregion": subregion}},
                                    {"$group": {"_id": subregion, "countriesCount": {operation: 1}}}]  # average ??
                        result = list(collection.aggregate(pipeline))
                    else:
                        field = "$" + field
                        pipeline = [{"$match": {"subregion": subregion}},
                                    {"$group": {"_id": subregion, " Result": {operation: field}}}]
                        result = list(collection.aggregate(pipeline))
                else:
                    result = {"Ok": 0, "msg": "Operation Error please choice among: " + str(allowed_operation)}
            else:
                result = {"Ok": 0, "msg": "Subregion Error please choice among: " + str(subRegion_list[1:])}
        else:
            result = {"Ok": 0, "msg": "field Error please choice among: " + str(countable_field)}
    else:
        result = {"Ok": 0, "msg": "Region Error please choice among: " + str(regions_list[1:])}
    return jsonify(result)


# This URI allows to users to get a particular region(continent) field count or average. It uses like this:
# www.world.com/continent/<region>/<operation>/<field>, operation can be "count" or "average"
@app.route('/continent/<region>/<operation>/<field>', methods=['GET'])
def continentOperation(region, operation, field):
    countable_field = ['population', 'area', 'gini', 'countries']
    allowed_operation = ['count', 'average']
    if region in regions_list:
        if field in countable_field:
            if operation in allowed_operation:
                operation = "$sum" if operation == "count" else "$avg"
                if field == countable_field[-1]:  # field = "countries"
                    pipeline = [{"$match": {"region": region}},
                                {"$group": {"_id": region, "countriesCount": {operation: 1}}}]  # average ??
                    result = list(collection.aggregate(pipeline))
                else:
                    field = "$" + field
                    pipeline = [{"$match": {"region": region}},
                                {"$group": {"_id": region, "Result": {operation: field}}}]
                    result = list(collection.aggregate(pipeline))
            else:
                result = {"Ok": 0, "msg": "Operation Error please choice among: " + str(allowed_operation)}
        else:
            result = {"Ok": 0, "msg": "field Error please choice among: " + str(countable_field)}
    else:
        result = {"Ok": 0, "msg": "Region Error please choice among: " + str(regions_list[1:])}
    return jsonify(result)


# This URI allow to users to get a particular World field count or average. It uses like this:
# /world/<operation>/<field>, operation can be "count" or "average"
@app.route('/world/<operation>/<field>', methods=['GET'])
def wordOperation(operation, field):
    countable_field = ['population', 'area', 'gini', 'countries']
    allowed_operation = ['count', 'average']
    if field in countable_field:
        if operation in allowed_operation:
            operation = "$sum" if operation == "count" else "$avg"
            if field == countable_field[-1]:
                pipeline = [{"$match": {"region": {"$exists": 1}}},
                            {"$group": {"_id": field, "countriesCount": {operation: 1}}}]  # average ??
                result = list(collection.aggregate(pipeline))
            else:
                pipeline = [{"$match": {"region": {"$exists": 1}}},
                            {"$group": {"_id": field, "Result": {operation: "$" + field}}}]
                result = list(collection.aggregate(pipeline))
        else:
            result = {"Ok": 0, "msg": "Operation Error please choice among: " + str(allowed_operation)}
    else:
        result = {"Ok": 0, "msg": "field Error please choice among: " + str(countable_field)}
    return jsonify(result)


@app.route('/country/findOne', methods=['GET'])
def findOne():
    result = collection.find_one({}, {'name': 1, 'capital': 1, 'population': 1, 'region': 1, 'subregion': 1, "_id": 0})
    return jsonify(result)


@app.route('/countries/count', methods=['GET'])
def count():
    nb = collection.count_documents({})
    return jsonify({"CountriesNumber": str(nb)})


# you can update a country name with only /country/update/all'
@app.route('/country/update/<field>', methods=['PUT'])
def update(field):
    new = request.json
    name = new["name"]
    if field in field_list:
        value = new[field]
        if name and name in countries_list:  # if name is set and name belongs to countries on the collection
            research = collection.find_one({"name": name}, {"_id": 0})  # we don't return the id
            research[field] = value
            e = datetime.now()  # get the current date
            research["modificationDate"] = e.strftime("%d/%m/%Y")  # get the date of modification
            research["modificationHour"] = e.strftime("%H:%M:%S")  # get the hour of modification
            research["processed"] = "False"
            update_collection.insert_one(research)
            result = {"Ok": 1, "msg": "modify successfully"}
        else:
            result = {"Ok": 0, "msg": "The country doesn't exist on the collection"}
    else:
        result = {"Ok": 0, "msg": "The field doesn't exist"}
    return jsonify(result)


@app.route('/country/update/<field1>/<field2>', methods=['PUT'])
def update2(field1, field2):
    new = request.json
    name = new["name"]
    if name and name in countries_list:  # if name is set and name belongs to countries on the collection
        if field1 in field_list and field2 in field_list:
            value1 = new[field1]
            value2 = new[field2]
            research = collection.find_one({"name": name}, {"_id": 0})  # we don't return the id
            research[field1] = value1
            research[field2] = value2
            e = datetime.now()  # get the current date
            research["modificationDate"] = e.strftime("%d/%m/%Y")  # get the date of modification
            research["modificationHour"] = e.strftime("%H:%M:%S")  # get the hour of modification
            research["processed"] = "False"
            update_collection.insert_one(research)
            result = {"Ok": 1}
        else:
            result = {"Ok": 0, "msg": "The fields don't exist"}
    else:
        result = {"Ok": 0, "msg": "The country doesn't exist on the collection"}
    return jsonify(result)


@app.route('/country/update/all', methods=['PUT'])  # Put for update
def updateAll():
    new = request.json  # the new document to add
    if new["population"] and new["capital"] and new["area"] and new["newName"]:
        if new["name"] in countries_list:
            research = collection.find_one({"name": new["name"]}, {"_id": 0})  # we don't return the id
            research["population"] = new["population"]
            research["capital"] = new["capital"]
            research["area"] = new["area"]
            research["name"] = new["newName"]
            e = datetime.now()  # get the current date
            research["modificationDate"] = e.strftime("%d/%m/%Y")  # get the date of modification
            research["modificationHour"] = e.strftime("%H:%M:%S")  # get the hour of modification
            research["processed"] = "False"
            update_collection.insert_one(research)
            result = {"Ok": 1, "msg": "Fields update successfully"}
        else:
            result = {"Ok": 0, "msg": "The country doesn't exist on the collection"}
    else:
        result = {"Ok": 0, "msg": "Fill all the fields"}

    return jsonify(result)


@app.route('/add/country', methods=['POST'])
def addCountry():
    new = request.json
    update_collection.insert_one(new)
    return jsonify({"Ok": 1, "msg": "Country added Successfully"})


if __name__ == '__main__':
    app.run()

