MONGO_URL= 'localhost'
MONGO_DB = 'taobao'
MONGO_TABLE = 'product'



SERVICE_ARGS = []
SERVICE_ARGS.append('--load-images=no')  #关闭图片加载
SERVICE_ARGS.append('--disk-cache=yes')  #开启缓存
SERVICE_ARGS.append('--ignore-ssl-errors=true') #忽略https错误
KEYWORDS = '美食'