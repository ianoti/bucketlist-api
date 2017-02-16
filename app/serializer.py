from flask_restful import fields

# Serialiser that converts model attributes to fields for display in a
# json format for item model
itemformat = {"id": fields.Integer,
              "name": fields.String,
              "date_created": fields.DateTime(dt_format="rfc822"),
              "date_modified": fields.DateTime(dt_format="rfc822"),
              "done": fields.Boolean(attribute="status")}
# Serialiser that converts model attributes to fields for display in a
# json format for bucketlist model
bucketlistformat = {"id": fields.Integer,
                    "name": fields.String,
                    "items": fields.List(fields.Nested(itemformat)),
                    "date_created": fields.DateTime(dt_format="rfc822"),
                    "date_modified": fields.DateTime(dt_format="rfc822"),
                    "created_by": fields.String(attribute="user.username")}
