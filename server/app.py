#!/usr/bin/env python3

from models import db, Sweet, Vendor, VendorSweet
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os
from flask import jsonify, abort
from flask import request

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return '<h1>Code challenge</h1>'

@app.route('/vendors', methods=['GET'])
def get_vendors():
    vendors = Vendor.query.all()
    vendor_data = [{'id': vendor.id, 'name': vendor.name} for vendor in vendors]
    return jsonify(vendor_data)

@app.route('/vendors/<int:vendor_id>', methods=['GET'])
def get_vendor(vendor_id):
    vendor = Vendor.query.get(vendor_id)
    if vendor is None:
        return jsonify({'error': 'Vendor not found'}), 404
    
    vendor_data = {
        'id': vendor.id,
        'name': vendor.name,
        'vendor_sweets': []
    }

    for vendor_sweet in vendor.vendor_sweets:
        sweet_data = {
            'id': vendor_sweet.id,
            'price': vendor_sweet.price,
            'sweet': {
                'id': vendor_sweet.sweet.id,
                'name': vendor_sweet.sweet.name
            },
            'sweet_id': vendor_sweet.sweet_id,
            'vendor_id': vendor_sweet.vendor_id
        }
        vendor_data['vendor_sweets'].append(sweet_data)
    
    return jsonify(vendor_data)

@app.route('/sweets', methods=['GET'])
def get_sweets():
    sweets = Sweet.query.all()
    sweet_data = [{'id': sweet.id, 'name': sweet.name} for sweet in sweets]
    return jsonify(sweet_data)

@app.route('/sweets/<int:sweet_id>', methods=['GET'])
def get_sweet(sweet_id):
    sweet = Sweet.query.get(sweet_id)
    if sweet is None:
        return jsonify({'error': 'Sweet not found'}), 404
    
    sweet_data = {
        'id': sweet.id,
        'name': sweet.name
    }

    return jsonify(sweet_data)

@app.route('/vendor_sweets', methods=['POST'])
def create_vendor_sweet():
    data = request.get_json()
    if not data or 'price' not in data or data['price'] < 0:
        return jsonify({'errors': ['validation errors']}), 400
    
    sweet_id = data.get('sweet_id')
    vendor_id = data.get('vendor_id')

    sweet = Sweet.query.get(sweet_id)
    vendor = Vendor.query.get(vendor_id)

    if not sweet:
        return jsonify({'errors': ['Sweet not found']}), 400
    
    if not vendor:
        return jsonify({'errors': ['Vendor not found']}), 400

    vendor_sweet = VendorSweet(price=data['price'], sweet=sweet, vendor=vendor)
    db.session.add(vendor_sweet)
    db.session.commit()

    return jsonify({
        'id': vendor_sweet.id,
        'price': vendor_sweet.price,
        'sweet': {
            'id': sweet.id,
            'name': sweet.name
        },
        'sweet_id': sweet.id,
        'vendor': {
            'id': vendor.id,
            'name': vendor.name
        },
        'vendor_id': vendor.id
    }), 201

@app.route('/vendor_sweets/<int:vendor_sweet_id>', methods=['DELETE'])
def delete_vendor_sweet(vendor_sweet_id):
    vendor_sweet = VendorSweet.query.get(vendor_sweet_id)
    if not vendor_sweet:
        return jsonify({'error': 'VendorSweet not found'}), 404

    db.session.delete(vendor_sweet)
    db.session.commit()

    return '', 204


if __name__ == '_main_':
    app.run(port=5555, debug=True)