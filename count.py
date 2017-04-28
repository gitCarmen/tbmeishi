from config import *
import pymongo
from spider import product_table

print(product_table.find().count())