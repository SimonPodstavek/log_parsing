import os
import pymongo
import dnspython
cluster="mongodb+srv://spodstavek:@cluster0.1ctzpcl.mongodb.net/?retryWrites=true&w=majority".format(os.getenv("HMH_MONGO_LOG_USER"))
