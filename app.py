from flask import Flask, render_template, url_for, request, redirect

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/model/<string:model>')
def model(model=None):
    '''
    Return a model's page.

    <model> is one of: player, team or nationality, or match
    '''
    # TODO: Load data from the DB
    # TODO: 404 if the model does not exist
    return render_template('model.html', model=model)


@app.route('/instance/<string:model>/<int:id>')
def instance(model=None, id=0):
    '''
    Return a instance's page.

    <model> is one of: player, team or nationality, or match
    <id> is the integer id of the specific instance
    '''
    # TODO: Load data from the DB
    # TODO: 404 if the model or id do not exist
    # TODO: The templates may need to be split up for each model
    return render_template('instance.html', model=model, id=id)


if __name__ == '__main__':
    app.run(debug=True)
