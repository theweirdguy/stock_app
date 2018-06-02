import os.path
import redis
import jinja2
import cherrypy



#jinja2 template renderer
root_path = os.path.dirname(__file__)
env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(root_path, 'templates')))


def render_template(template, **context):
    global env
    template = env.get_template(template + '.jinja')
    return template.render(context)


class StockListRedisService(object):

    connection = redis.Redis('localhost')

    def get_stock_list(self):
        data_list = []
        key_list = self.get_topstocks()

        for key in key_list:
            data = self.connection.lrange(key, 0, - 1)
            data.insert(0,key)
            data_list.append([i.decode('UTF-8') if not isinstance(i, str) else i for i in data])
        return data_list

    def get_topstocks(self):
        top_stock_key = self.connection.zrange("stock_rank", 0, 9)
        return [i.decode('UTF-8') for i in top_stock_key]

    def get_specific_stock(self, query_stock):
        data=self.connection.lrange(query_stock, 0, -1)
        data.insert(0, query_stock)
        return [i.decode('UTF-8') if not isinstance(i, str) else i for i in data]


class StockListGenerator(object):

    stock_service = StockListRedisService()

    @cherrypy.expose
    def index(self):
        stock_list = self.stock_service.get_stock_list()
        return render_template('index', stock_list=stock_list)

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

    cherrypy.config.update({'server.socket_host': '0.0.0.0', })
    cherrypy.config.update({'server.socket_port': int(os.environ.get('PORT', '5000')), })
    webapp = StockListGenerator()
    cherrypy.quickstart(webapp, '/', conf)
