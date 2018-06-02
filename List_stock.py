import os, os.path
import redis
import jinja2
import cherrypy



"""
This is the template library Jinja2, as I acquainted with it when I used Django.
Just to add CherryPy is sweet.
"""
root_path = os.path.dirname(__file__)
env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(root_path, 'templates')))


def render_template(template, **context):
    global env
    template = env.get_template(template + '.jinja')
    return template.render(context)

"""
The class for all the Redis Databse opearations.
"""
class StockListRedisService(object):

    connection = redis.Redis('localhost')
    #connection = redis.from_url(os.environ.get("REDIS_URL"))

    """
    Get me the list of all the 10 ten stocks of the day.
    """
    def get_stock_list(self):
        data_list = []
        key_list = self.get_topstocks()

        for key in key_list:
            data = self.connection.lrange(key, 0, - 1)
            data.insert(0,key)
            data_list.append([i.decode('UTF-8') if not isinstance(i, str) else i for i in data])
        return data_list

    """
    Get me the key for the top stocks which is the name of the companies
    stored as ordered set with rank as the differece of the opening and 
    closing values of the day.
    """
    def get_topstocks(self):
        top_stock_key = self.connection.zrange("stock_rank", 0, 9)
        return [i.decode('UTF-8') for i in top_stock_key]

    """
    Get a specific stock for the earched query of user.
    """
    def get_specific_stock(self, query_stock):
        data=self.connection.lrange(query_stock, 0, -1)
        data.insert(0, query_stock)
        return [i.decode('UTF-8') if not isinstance(i, str) else i for i in data]


class StockListGenerator(object):

    stock_service = StockListRedisService()

    """
    View fumction for the listing of top ten stocks.
    """
    @cherrypy.expose
    def index(self):
        stock_list = self.stock_service.get_stock_list()
        return render_template('index', stock_list=stock_list)

    """
    View funciton for the listing of specific stocks.
    """
    @cherrypy.expose
    def search_stocks(self, search):
        specific_stock_list = self.stock_service.get_specific_stock(search)
        return render_template('stock_specific', specific_stock_list=specific_stock_list)


if __name__ == '__main__':
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        }
    }

    """
    COnfiguration for heroku
    """
    cherrypy.config.update({'server.socket_host': '0.0.0.0', })
    cherrypy.config.update({'server.socket_port': int(os.environ.get('PORT', '5000')), })

    webapp = StockListGenerator()
    cherrypy.quickstart(webapp, '/', conf)
