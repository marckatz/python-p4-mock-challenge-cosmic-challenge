#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class Scientists(Resource):
    def get(self):
        scientists = [sci.to_dict(rules=('-missions',)) for sci in Scientist.query.all()]
        return make_response(scientists,200)
    
    def post(self):
        try:
            data = request.get_json()
            new_scientist = Scientist(
                name = data['name'],
                field_of_study = data['field_of_study']
            )
            db.session.add(new_scientist)
            db.session.commit()

            return make_response(new_scientist.to_dict(),201)
        except:
            return make_response({"errors": ["validation errors"]}, 400)
    
api.add_resource(Scientists, '/scientists')

class ScientistsById(Resource):
    def get(self, id):
        try:
            scientist = Scientist.query.filter_by(id = id).first()
            return make_response(scientist.to_dict(), 200)
        except:
            return make_response({"error": "Scientist not found"}, 404)
    
    def patch(self, id):
        try:
            scientist = Scientist.query.filter_by(id = id).first()
            data = request.get_json()
            for attr in data:
                setattr(scientist, attr, data[attr])
            db.session.commit()
            return make_response(scientist.to_dict(),202)
        except AttributeError:
            return make_response({"error": "Scientist not found"}, 404)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)
        except Exception as e:
            return make_response({'error':f'wtf did you do {e}'}, 420)

    def delete(self, id):
        from sqlalchemy.orm.exc import UnmappedInstanceError
        try:
            scientist = Scientist.query.filter_by(id = id).first()
            db.session.delete(scientist)
            db.session.commit()
            return make_response({},204)
        except UnmappedInstanceError:
            return make_response({"error": "Scientist not found"}, 404)

api.add_resource(ScientistsById, '/scientists/<int:id>')






if __name__ == '__main__':
    app.run(port=5555, debug=True)
