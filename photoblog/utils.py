from werkzeug import Local, LocalManager

local = Local()
local_manager = LocalManager([local])
application = local('application')
db = local('db')

