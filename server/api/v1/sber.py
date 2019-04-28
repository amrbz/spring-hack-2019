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

sber = Blueprint('sber_v1', url_prefix='/sber')
sber_cypher = Blueprint('sber_cypher_v1', url_prefix='/sber_cypher')

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


class Sber(HTTPMethodView):

    def post(self, request):
    
        if 'passport' not in request.form:
            return bad_request('Passport number is not provided')

        if 'publicKey' not in request.form:
            return bad_request('Public key is not provided')

        passport = request.form['passport'][0]
        public_key = request.form['publicKey'][0]

        if passport == '':
            return bad_request('Passport is not provided')
        
        if public_key == '':
            return bad_request('Public key is not provided')

        try:
            conn = psycopg2.connect(**dsn)
            with conn:
                with conn.cursor() as cur:
                    reset_id = str(uuid.uuid4())
                    cur.execute("""
                        INSERT INTO resets (id, passport, public_key, verified)
                        VALUES ('{id}', '{passport}', '{public_key}', '{verified}')
                    """.format(
                            id=reset_id,
                            passport=passport.replace('\n', ''),
                            public_key=public_key.replace('\n', ''),
                            verified=0
                        ))

                    conn.commit()
        except Exception as error:
            logger.error(error)
            return bad_request(error)

        data = {
            'id': reset_id,
            'passport': passport,
            'publicKey': public_key
        }

        return json(data, status=201)


    def get(self, requests):
        try:
            conn = psycopg2.connect(**dsn)
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, passport, public_key, cypher_text, verified
                        FROM resets
                        ORDER BY timestamp DESC
                    """)
                    resets = cur.fetchall()

        except Exception as error:
            logger.error(error)
            return bad_request(error)

        data = [{
            'id': el[0],
            'passport': el[1],
            'publicKey': el[2],
            'cypherText': el[3],
            'verified': int(el[4]) == 1
        } for el in resets]
        
        return json(data, status=200)


    def put(self, request):
    
        if 'publicKey' not in request.form:
            return bad_request('Public Key is not provided')

        public_key = request.form['publicKey'][0]

        print('publicKey', public_key)

        try:
            conn = psycopg2.connect(**dsn)
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE resets SET verified=1
                        WHERE public_key='{public_key}'
                    """.format(
                            public_key=public_key.replace('\n', ''),
                        ))

                    conn.commit()
        except Exception as error:
            logger.error(error)
            return bad_request(error)

        data = {
            'publicKey': public_key,
            'verified': True
        }

        return json(data, status=200)



class SberCypher(HTTPMethodView):

    def get(self, requests, passport):

        try:
            conn = psycopg2.connect(**dsn)
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT COUNT(*)
                        FROM resets
                        WHERE passport='{passport}'
                        AND verified=1
                    """.format(
                        passport=passport
                    ))
                    count = cur.fetchone()[0]
                    if count == 0:
                        return bad_request('No verified requests. Please contact bank manager.')

                    cur.execute("""
                        SELECT id, passport, public_key, cypher_text
                        FROM resets
                        WHERE passport='{passport}'
                    """.format(
                        passport=passport
                    ))
                    resets = cur.fetchone()

        except Exception as error:
            logger.error(error)
            return bad_request(error)

        data = {
            'id': resets[0],
            'passport': resets[1],
            'publicKey': resets[2],
            'cypherText': resets[3]
        }
        
        return json(data, status=200)


    def put(self, request):
    
        if 'cypherText' not in request.form:
            return bad_request('Cypher text is not provided')

        if 'publicKey' not in request.form:
            return bad_request('publicKey text is not provided')
        

        # if 'id' not in request.form:
        #     return bad_request('Reset ID key is not provided')

        cypher_text = request.form['cypherText'][0]
        # reset_id = request.form['id'][0]
        public_key = request.form['publicKey'][0]

        try:
            conn = psycopg2.connect(**dsn)
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT COUNT(*)
                        FROM resets
                        WHERE verified=1
                        AND public_key='{public_key}'
                    """.format(
                        public_key=public_key.replace('\n', '')
                    ))
                    count = cur.fetchone()[0]
                    if count == 0:
                        return bad_request('Reset ID is not confirmed by bank manager')

                    cur.execute("""
                        UPDATE resets SET cypher_text='{cypher_text}'
                        WHERE public_key='{public_key}'
                    """.format(
                            public_key=public_key.replace('\n', ''),
                            cypher_text=cypher_text.replace('\n', '')
                        ))

                    conn.commit()
        except Exception as error:
            logger.error(error)
            return bad_request(error)

        data = {
            'cypherText': cypher_text,
            'id': public_key
        }

        return json(data, status=200)


sber.add_route(Sber.as_view(), '/')
sber_cypher.add_route(SberCypher.as_view(), '/')
sber_cypher.add_route(SberCypher.as_view(), '/<passport>')