from sanic import Sanic
import os
from sanic import Blueprint
from sanic.views import HTTPMethodView
from sanic.response import text
from sanic.log import logger
from sanic.response import json
import uuid
import asyncio
import aiohttp
import requests
import psycopg2
from .errors import bad_request
import configparser
import base58
import pywaves as pw

qr = Blueprint('qr_v1', url_prefix='/qr')
qr_verify = Blueprint('qr_verify_v1', url_prefix='/qr/verify')

config = configparser.ConfigParser()
config.read('config.ini')

dsn = {
    "user": config['DB']['user'],
    "password": config['DB']['password'],
    "database": config['DB']['database'],
    "host": config['DB']['host'],
    "port": config['DB']['port'],
    "sslmode": config['DB']['sslmode']
}


class Qr(HTTPMethodView):

    def post(self, request):
    
        if 'passport' not in request.form:
            return bad_request('Passport number is not provided')

        if 'secret' not in request.form:
            return bad_request('Secret is not provided')

        passport = request.form['passport'][0]
        secret = request.form['secret'][0]

        if passport == '':
            return bad_request('Passport is not provided')
        
        if secret == '':
            return bad_request('Secret is not provided')

        try:
            conn = psycopg2.connect(**dsn)
            with conn:
                with conn.cursor() as cur:
                    qr_id = str(uuid.uuid4())
                    cur.execute("""
                        INSERT INTO qr (id, passport, secret)
                        VALUES ('{id}', '{passport}', '{secret}')
                    """.format(
                            id=qr_id,
                            passport=passport.replace('\n', ''),
                            secret=secret.replace('\n', ''),
                        ))

                    conn.commit()
        except Exception as error:
            logger.error(error)
            return bad_request(error)

        data = {
            'id': qr_id,
            'passport': passport,
            'secret': secret
        }

        return json(data, status=201)


    def get(self, requests):
        try:
            conn = psycopg2.connect(**dsn)
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, passport, secret, qr_code, verified
                        FROM qr
                        ORDER BY timestamp DESC
                    """)
                    resets = cur.fetchall()

        except Exception as error:
            logger.error(error)
            return bad_request(error)

        data = [{
            'id': el[0],
            'passport': el[1],
            'secret': el[2],
            'qrCode': el[3],
            'verified': int(el[4]) == 1
        } for el in resets]
        
        return json(data, status=200)


    def put(self, request):
    
        if 'id' not in request.form:
            return bad_request('ID number is not provided')

        if 'qrCode' not in request.form:
            return bad_request('QR Code is not provided')

        qr_id = request.form['id'][0]
        qr_code = request.form['qrCode'][0]

        try:
            conn = psycopg2.connect(**dsn)
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE qr SET verified=1, qr_code='{qr_code}'
                        WHERE id='{id}'
                    """.format(
                            id=qr_id,
                            qr_code=qr_code.replace('\n', '')
                        ))

                    conn.commit()
        except Exception as error:
            logger.error(error)
            return bad_request(error)

        data = {
            'id': qr_id,
            'qrCode': qr_code,
            'verified': True
        }

        return json(data, status=200)


class QrVerify(HTTPMethodView):

    def get(self, requests, qr_id):
        try:
            conn = psycopg2.connect(**dsn)
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT COUNT(*)
                        FROM qr
                        WHERE id='{qr_id}'
                        AND verified=1
                    """.format(
                        qr_id=qr_id
                    ))
                    count = cur.fetchone()[0]
                    if count == 0:
                        return bad_request('ID is not confirmed by manager')

                    cur.execute("""
                        SELECT id, passport, secret, qr_code, verified
                        FROM qr
                        WHERE id='{qr_id}'
                    """.format(
                        qr_id=qr_id
                    ))
                    qr_data = cur.fetchone()

        except Exception as error:
            logger.error(error)
            return bad_request(error)

        if not qr_data:
            bad_request('No data found by provided ID')

        data = {
            # 'id': qr_data[0],
            # 'passport': qr_data[1],
            'secret': qr_data[2],
            # 'qrCode': qr_data[3],
            # 'verified': int(qr_data[4]) == 1
        }
        
        return json(data, status=200)


qr.add_route(Qr.as_view(), '/')
qr_verify.add_route(QrVerify.as_view(), '/<qr_id>')