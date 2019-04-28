from sanic import Blueprint
from .sber import sber
from .sber import sber_cypher
from .qr import qr
from .qr import qr_verify

api_v1 = Blueprint.group(
  sber,
  sber_cypher,
  qr,
  qr_verify,
  url_prefix='/v1'
)


