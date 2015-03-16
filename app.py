from flask import Flask, request, jsonify
from flask.ext import restful
import LocData
from datetime import datetime

app = Flask(__name__)
api = restful.Api(app)


class getStatus(restful.Resource):
    def formReply(self, results):
        parsed = {"Hits": []}
        print("We will surviveee..")
        for x in results:
            parsed["Hits"].append({"GPS": x[0], "Date": x[1], "City": x[2]})
        for x in parsed:
            print(x)
        return jsonify({"Hits": parsed["Hits"]})

    def query(self, query):
        with open("FI.txt", 'r', encoding="UTF-8") as db:
            # print("Toimii vielä")
            user = "default"
            area = []
            between = []
            if "user" in query:
                user = query["user"]
            if "dates" in query:
                date = query["dates"]
                date[0] = date[0].split("-")
                date[1] = date[1].split("-")
                date1 = datetime(int(date[0][0]), int(date[0][1].lstrip("0")), int(date[0][2].lstrip("0")))
                date2 = datetime(int(date[1][0]), int(date[1][1].lstrip("0")), int(date[1][2].lstrip("0")))
                between = [date1, date2]
                print(between)
            if "areas" in query:
                print(query)
                for a in query["areas"]:
                    if a == "None":
                        area.append(None)
                    else:
                        print("a is: {}".format(a))
                        coords = a.replace(" ", "").split(",")
                        print("Coords: {}".format(coords))
                        area.append([float(coords[0]), float(coords[1]), float(coords[2])])
            print("We got area :{} \nWe got time span:{} ".format(area, between))
            loc = LocData.LocData(db, user)
            results = loc.getData(between, area)
            return self.formReply(results)

    '''
    get(self)
        In this function we define behaviour for GET requests. The current behaviour is set to run the LocData tests()
        function and return JSONified version of the output.
    '''
    def get(self):
        with open("FI.txt", 'r', encoding="UTF-8") as db:
            loc = LocData.LocData(db, "blabla")
            loc = loc.tests()
            print("Working!")
            return self.formReply(loc)

        return {"status": "Working!"}
    '''
    put(self)
        In this function we define behaviour for PUT request. We expect data containing parameters for a lookup in
        from LocData, formatted in JSON as:
        Using curl an example could be:
         curl -i -H "Content-Type: application/json" -X PUT -d '{"dates": ["2014-01-13","2015-03-24"], "areas": ["60.852269,0,21.632595", "60.891876,0,21.74263", "None"] }' hostaddress
    '''
    def put(self):
        for x in request.json:
            print(x)
        user = "default"
        if not request.json:
            abort(400)
        between = request.json["dates"]
        area = request.json["areas"]
        print("We got: {} as dates and {} as areas".format(between[1], area))
        return self.query(request.json)


api.add_resource(getStatus, '/')

if __name__ == '__main__':
    app.run(host="0.0.0.0")
