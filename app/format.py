from flask_restful import fields

itemformat = {"id": fields.Integer,
              "name": fields.String,
              "date_created": fields.DateTime(dt_format="rfc822"),
              "date_modified": fields.DateTime(dt_format="rfc822"),
              "done": fields.Boolean(attribute="status")}

bucketlistformat = {"id": fields.Integer,
                    "name": fields.String,
                    "items": fields.List(fields.Nested(itemformat)),
                    "date_created": fields.DateTime(dt_format="rfc822"),
                    "date_modified": fields.DateTime(dt_format="rfc822"),
                    "created_by": fields.String(attribute="user.username")}

# allbucketlistformat = {
#     "bucketlists": fields.List(fields.Nested(bucketlistformat))
# }

# allitemsformat = {
#     "items": fields.List(fields.Nested(itemformat))
# }
