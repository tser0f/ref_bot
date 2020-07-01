from configparser import ConfigParser

_environment = "dev"

ini_config = ConfigParser()

if _environment != "":
    ini_config.read('config.{0}.ini'.format(_environment))
else:
    ini_config.read('config.ini')

