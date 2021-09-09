import ast

import pandas as pd
from flask import Flask
from flask_restful import Api, Resource, reqparse

app = Flask(__name__)
api = Api(app)


class Users(Resource):
    def get(self):
        # read local CSV
        data = pd.read_csv("../users.csv")

        # convert dataframe to dict
        data = data.to_dict()

        # return data and 200 OK
        return {"data": data}, 200

    def post(self):

        # initialize
        parser = reqparse.RequestParser()

        # add args
        parser.add_argument("userId", required=True)
        parser.add_argument("name", required=True)
        parser.add_argument("city", required=True)

        # parse arguments to dictionary
        args = parser.parse_args()

        # read our CSV
        data = pd.read_csv("../users.csv")

        if args["userId"] in list(data["userId"]):
            return {"message": f"'{args['userId']}' already exists."}, 409
        else:
            # create new dataframe containing new values
            new_data = pd.DataFrame(
                {
                    "userId": [args["userId"]],
                    "name": [args["name"]],
                    "city": [args["city"]],
                    "locations": [[]],
                }
            )

            # add the newly provided values
            data = data.append(new_data, ignore_index=True)

            # save back to CSV
            data.to_csv("../users.csv", index=False)

            # return data with 200 OK
            return {"data": data.to_dict()}, 200

    def put(self):
        # initialize
        parser = reqparse.RequestParser()

        # add args
        parser.add_argument("userId", required=True)
        parser.add_argument("location", required=True)

        # parse arguments to dictionary
        args = parser.parse_args()

        # read our CSV
        data = pd.read_csv("../users.csv")

        if args["userId"] in list(data["userId"]):
            # evaluate strings of lists to lists !!! never put something like this in prod
            data["locations"] = data["locations"].apply(lambda x: ast.literal_eval(x))

            # select our user
            user_data = data[data["userId"] == args["userId"]]

            # update user's locations
            user_data["locations"] = (
                user_data["locations"].values[0].append(args["location"])
            )

            # save back to CSV
            data.to_csv("../users.csv", index=False)

            # return data and 200 OK
            return {"data": data.to_dict()}, 200

        else:
            # otherwise the userId does not exist
            return {"message": f"'{args['userId']}' user not found."}, 404

    def delete(self):
        # initialize
        parser = reqparse.RequestParser()

        # add userId arg
        parser.add_argument("userId", required=True)

        # parse arguments to dictionary
        args = parser.parse_args()

        # read our CSV
        data = pd.read_csv("../users.csv")

        if args["userId"] in list(data["userId"]):
            # remove data entry matching given userId
            data = data[data["userId"] != args["userId"]]

            # save back to CSV
            data.to_csv("../users.csv", index=False)

            # return data and 200 OK
            return {"data": data.to_dict()}, 200
        else:
            # otherwise we return 404 because userId does not exist
            return {"message": f"'{args['userId']}' user not found."}, 404


class Locations(Resource):
    def get(self):
        # read local CSV
        data = pd.read_csv("../locations.csv")

        # return data dict and 200 OK
        return {"data": data.to_dict()}, 200

    def post(self):
        # initialize parser
        parser = reqparse.RequestParser()

        # add args
        parser.add_argument("locationId", required=True, type=int)
        parser.add_argument("name", required=True)
        parser.add_argument("rating", required=True)

        # parse arguments to dictionary
        args = parser.parse_args()

        # read our CSV
        data = pd.read_csv("../locations.csv")

        # check if location already exists
        if args["locationId"] in list(data["locationId"]):
            # if locationId already exists, return 401 unauthorized
            return {"message": f"'{args['locationId']}' already exists."}, 409
        else:
            # otherwise, we can add the new location record
            # create new dataframe containing new values
            new_data = pd.DataFrame(
                {
                    "locationId": [args["locationId"]],
                    "name": [args["name"]],
                    "rating": [args["rating"]],
                }
            )

            # add the newly provided values
            data = data.append(new_data, ignore_index=True)

            # save back to CSV
            data.to_csv("../locations.csv", index=False)

            # return data with 200 OK
            return {"data": data.to_dict()}, 200

    def patch(self):
        # initialize parser
        parser = reqparse.RequestParser()

        # add args
        parser.add_argument("locationId", required=True, type=int)
        parser.add_argument("name", store_missing=False)  # name/rating are optional
        parser.add_argument("rating", store_missing=False)

        # parse arguments to dictionary
        args = parser.parse_args()

        # read our CSV
        data = pd.read_csv("../locations.csv")

        # check that the location exists
        if args["locationId"] in list(data["locationId"]):
            # if it exists, we can update it, first we get user row
            user_data = data[data["locationId"] == args["locationId"]]

            # if name has been provided, we update name
            if "name" in args:
                user_data["name"] = args["name"]
            # if rating has been provided, we update rating
            if "rating" in args:
                user_data["rating"] = args["rating"]

            # update data
            data[data["locationId"] == args["locationId"]] = user_data

            # now save updated data
            data.to_csv("../locations.csv", index=False)

            # return data and 200 OK
            return {"data": data.to_dict()}, 200

        else:
            # otherwise we return 404 not found
            return {"message": f"'{args['locationId']}' location does not exist."}, 404

    def delete(self):
        # initialize parser
        parser = reqparse.RequestParser()

        # add locationId arg
        parser.add_argument("locationId", required=True, type=int)

        # parse arguments to dictionary
        args = parser.parse_args()

        # read our CSV
        data = pd.read_csv("../locations.csv")

        # check that the locationId exists
        if args["locationId"] in list(data["locationId"]):
            # if it exists, we delete it
            data = data[data["locationId"] != args["locationId"]]

            # save the data
            data.to_csv("../locations.csv", index=False)

            # return data and 200 OK
            return {"data": data.to_dict()}, 200

        else:
            # otherwise we return 404 not found
            return {"message": f"'{args['locationId']}' location does not exist."}, 404


# add endpoints
api.add_resource(Users, "/users")
api.add_resource(Locations, "/locations")

if __name__ == "__main__":
    # run the Flask app
    app.run()
