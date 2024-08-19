from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import date, datetime, timedelta

from replit.object_storage import Client
client = Client()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

class Symbol(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False, unique=True)
    total_score = db.Column(db.Integer, nullable=False)
    growth = db.Column(db.Integer, nullable=False)
    dividends = db.Column(db.Integer, nullable=False)
    health = db.Column(db.Integer, nullable=False)
    gnumber = db.Column(db.Integer, nullable=False)
    marketcap = db.Column(db.Integer, nullable=False)


class GrowthData(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  symbol = db.Column(db.String(10), db.ForeignKey('symbol.symbol'), nullable=False)
  growth_value = db.Column(db.Integer, nullable=False)


class DividendsData(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  symbol = db.Column(db.String(10), db.ForeignKey('symbol.symbol'), nullable=False)
  dividend_value = db.Column(db.Integer, nullable=False)


class HealthData(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  symbol = db.Column(db.String(10), db.ForeignKey('symbol.symbol'), nullable=False)
  health_value = db.Column(db.Integer, nullable=False)


class GNumberData(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  symbol = db.Column(db.String(10), db.ForeignKey('symbol.symbol'), nullable=False)
  gnumber_value = db.Column(db.Float, nullable=False)  # Use Float for decimal values
  current_price = db.Column(db.Float, nullable=False)
  score = db.Column(db.Integer, nullable=False)


class MarketcapData(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  symbol = db.Column(db.String(10), db.ForeignKey('symbol.symbol'), nullable=False)
  marketcap_value = db.Column(db.Integer, nullable=False)


@app.route('/growth_data', methods=['POST'])
def post_growth_data():
    data = request.json
    for item in data:
        new_growth = GrowthData(symbol=item['symbol'], growth_value=item['growth_value'])
        db.session.add(new_growth)
    db.session.commit()
    return jsonify({"message": "Growth data added successfully!"}), 201


@app.route('/dividends_data', methods=['POST'])
def post_dividends_data():
    data = request.json
    for item in data:
        new_dividends = DividendsData(symbol=item['symbol'], dividend_value=item['dividend_value'])
        db.session.add(new_dividends)
    db.session.commit()
    return jsonify({"message": "Dividends data added successfully!"}), 201


@app.route('/health_data', methods=['POST'])
def post_health_data():
    data = request.json
    for item in data:
        new_health = HealthData(symbol=item['symbol'], health_value=item['health_value'])
        db.session.add(new_health)
    db.session.commit()
    return jsonify({"message": "Health data added successfully!"}), 201


@app.route('/gnumber_data', methods=['POST'])
def post_gnumber_data():
    data = json.loads(request.data.decode('utf-8'))
    for ticker, gnumber_data in data.items():
        ticker = GNumberData(
            symbol=gnumber_data['ticker'],
            gnumber_value=gnumber_data['GNumber'],
            current_price=gnumber_data['Current Price'],
            score=gnumber_data['score']
        )
        db.session.add(ticker)
    db.session.commit()
    return jsonify({"message": "G-Number data added successfully!"}), 201


@app.route('/common_symbols', methods=['POST'])
def common_symbols():
    data = json.loads(request.data.decode('utf-8'))  # Decoding and loading the JSON data

    client.upload_from_text("common_symbols.json", data)

    return jsonify({"message": "Symbols database updated successfully!"}), 200


@app.route('/marketcap_data', methods=['POST'])
def post_marketcap_data():
    data = request.json
    for item in data:
        new_marketcap = MarketcapData(symbol=item['symbol'], marketcap_value=item['marketcap_value'])
        db.session.add(new_marketcap)
    db.session.commit()
    return jsonify({"message": "Marketcap data added successfully!"}), 201


@app.route('/get_growth_data', methods=['GET'])
def get_growth_data():
    growth_data = GrowthData.query.all()
    return jsonify([{'symbol': growth.symbol, 'growth_value': growth.growth_value} for growth in growth_data])


@app.route('/get_dividends_data', methods=['GET'])
def get_dividends_data():
    dividends_data = DividendsData.query.all()
    return jsonify([{'symbol': dividend.symbol, 'dividend_value': dividend.dividend_value} for dividend in dividends_data])


@app.route('/get_health_data', methods=['GET'])
def get_health_data():
    health_data = HealthData.query.all()
    return jsonify([{'symbol': health.symbol, 'health_value': health.health_value} for health in health_data])


@app.route('/get_gnumber_data', methods=['GET'])
def get_gnumber_data():
    gnumber_data = GNumberData.query.all()
    return jsonify([{'symbol': gnumber.symbol, 'gnumber_value': gnumber.gnumber_value} for gnumber in gnumber_data])


@app.route('/get_marketcap_data', methods=['GET'])
def get_marketcap_data():
    marketcap_data = MarketcapData.query.all()
    return jsonify([{'symbol': marketcap.symbol, 'marketcap_value': marketcap.marketcap_value} for marketcap in marketcap_data])


@app.route('/user', methods=['POST'])
def add_user():
    data = request.json
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already exists!"}), 400
    else:
        new_user = User(username=data['username'], email=data['email'])
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User created!"}), 201

  
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{'id': user.id, 'username': user.username, 'email': user.email} for user in users])


@app.route('/get_subscribers', methods=['GET'])
def get_subscribers():
    subscribers = User.query.all()
    subscribers_data = [{'id': subscriber.id, 'username': subscriber.username, 'email': subscriber.email} for subscriber in subscribers]
    return jsonify(subscribers_data)


@app.route('/get_common_symbols', methods=['GET'])
def get_common_symbols():
    # Fetching common_symbols.json content from object storage
    symbols_data = client.download_as_text("common_symbols.json")
    return symbols_data, 200


@app.route('/subscribers', methods=['POST'])
def manage_subscribers():
    subscribers = request.json
    current_emails = [subscriber['email'] for subscriber in subscribers]

    # Query users whose emails are not in the current_emails list
    users_to_delete = User.query.filter(User.email.notin_(current_emails)).all()

    added_count = 0
    updated_count = 0
    deleted_count = 0

    for subscriber in subscribers:
        user = User.query.filter_by(email=subscriber['email']).first()
        if user:
            user.username = subscriber['name']
            updated_count += 1
        else:
            new_user = User(username=subscriber['name'], email=subscriber['email'])
            db.session.add(new_user)
            added_count += 1

    for user in users_to_delete:
        db.session.delete(user)
        deleted_count += 1

    db.session.commit()
    return jsonify({"message": f"{added_count} subscribers added, {updated_count} updated, {deleted_count} deleted successfully!"}), 201


@app.route('/test')
def test():
    # GNumberData.query.delete()
    # db.session.commit()
    # Get all data from all models
    symbols = Symbol.query.all()
    growth_data = GrowthData.query.all()
    dividends_data = DividendsData.query.all()
    health_data = HealthData.query.all()
    gnumber_data = GNumberData.query.all()
    marketcap_data = MarketcapData.query.all()
    users = User.query.all()
    # Format data for display
    database_content = {
        'symbols': [
            {'id': symbol.id, 'symbol': symbol.symbol, 'total_score': symbol.total_score, 
             'growth': symbol.growth, 'dividends': symbol.dividends, 'health': symbol.health,
             'gnumber': symbol.gnumber, 'marketcap': symbol.marketcap}
            for symbol in symbols
        ],
        'growth_data': [
            {'id': growth.id, 'symbol': growth.symbol, 'growth_value': growth.growth_value}
            for growth in growth_data
        ],
        'dividends_data': [
            {'id': dividend.id, 'symbol': dividend.symbol, 'dividend_value': dividend.dividend_value}
            for dividend in dividends_data
        ],
        'health_data': [
            {'id': health.id, 'symbol': health.symbol, 'health_value': health.health_value}
            for health in health_data
        ],
        'gnumber_data': [
            {'id': gnumber.id, 'symbol': gnumber.symbol, 'gnumber_value': gnumber.gnumber_value}
            for gnumber in gnumber_data
        ],
        'marketcap_data': [
            {'id': marketcap.id, 'symbol': marketcap.symbol, 'marketcap_value': marketcap.marketcap_value}
            for marketcap in marketcap_data
        ],
        'users': [
            {'id': user.id, 'username': user.username, 'email': user.email}
            for user in users
        ]
    }
    return render_template('test.html', database_content=database_content)
    # print(json.dumps(database_content, indent=4))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8080, debug=True)