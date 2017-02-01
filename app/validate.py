from flask_inputs import Inputs
from flask_inputs.validators import JsonSchema
# sample schema format
# schema = {
#   "name": {
#     "type": "string",
#     "required": True
#   },
#   "age": {
#     "type": "number",
#     "required": True
#     "maximum": 120,
#     "minimum": 0
#   }
# }
login = {
    "username": {"type": "string", "required": True},
    "password": {"type": "string", "required": True}
    }

class JsonInputs(Inputs):
    json = [JsonSchema(schema=login)]
