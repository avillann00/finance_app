# import the create app function
from website import create_app

# make the app
app = create_app()

# if this file is file is executed then run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
