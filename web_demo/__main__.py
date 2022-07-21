from .app import app

from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument('--port',  type=int, default=8050)

if __name__ == '__main__':
    args = parser.parse_args()
    port = args.port
    app.run(debug=False, port=port)