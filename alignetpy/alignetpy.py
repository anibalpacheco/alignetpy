# -*- coding: utf-8 -*-
# Copyright (C) 2014 G&D Systems S.A
# Developer: Dairon Medina Caro <info@gydsystems.com>

import random
import string
import binascii
import base64
import xml.etree.cElementTree as ET

import re

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Cipher import DES3
from Crypto import Random


class AlignetError(Exception):
    """
    Common alignet Exception
    """
    pass


class Alignet(object):
    """
    Alignet Payments Class
    """

    def create_xml(self, array):
        """
        Returns the xml response
        """
        valid_fields = [
            'acquirerId',
            'commerceId',
            'purchaseCurrencyCode',
            'purchaseAmount',
            'purchaseOperationNumber',
            'billingAddress',
            'billingCity',
            'billingState',
            'billingCountry',
            'billingZIP',
            'billingPhone',
            'billingEMail',
            'billingFirstName',
            'billingLastName',
            'language',
            'commerceMallId',
            'terminalCode',
            'tipAmount',
            'HTTPSessionId',
            'shippingAddress',
            'shippingCity',
            'shippingState',
            'shippingCountry',
            'shippingZIP',
            'shippingPhone',
            'shippingEMail',
            'shippingFirstName',
            'shippingLastName',
            'reserved1',
            'reserved2',
            'reserved3',
            'reserved4',
            'reserved5',
            'reserved6',
            'reserved7',
            'reserved8',
            'reserved9',
            'reserved10',
            'reserved11',
            'reserved12',
            'reserved13',
            'reserved14',
            'reserved15',
            'reserved16',
            'reserved17',
            'reserved18',
            'reserved19',
            'reserved20',
            'reserved21',
            'reserved22',
            'reserved23',
            'reserved24',
            'reserved25',
            'reserved26',
            'reserved27',
            'reserved28',
            'reserved29',
            'reserved30',
            'reserved31',
            'reserved32',
            'reserved33',
            'reserved34',
            'reserved35',
            'reserved36',
            'reserved37',
            'reserved38',
            'reserved39',
            'reserved40',
        ]

        root = ET.Element('VPOSTransaction1.2')

        temp_dict = dict()
        taxes = dict()
        taxes_vals = dict()

        for key, value in array.items():
            if key in valid_fields:
                temp_dict[key] = value
            elif re.search(r'tax_([0-9]{1}|[0-9]{2})_name', key):
                re.sub(r'(^tax_)|(_name$)', '', key)
                taxes[key] = value
            else:
                raise AlignetError('%s is not allowed value in Alignet.') % key

        for key, value in temp_dict.items():
            elem = ET.SubElement(root, key)
            elem.text = value

        #TODO: If some taxes exist add to the XML doc
        if len(taxes):
            pass

        return ET.tostring(root, encoding='iso-8859-1')

    def vpos_send(self, input_array, cipher_publickey, sign_privatekey, vector):
        """
        Send the data to VPOS
        @TODO: Document well this with sphinx
        """
        output_array = dict()

        output_xml = self.create_xml(input_array)

        sessionkey = self.generate_session_key()

        return output_array

    def vpos_response(self):
        """
        TODO: Finish this
        """
        raise NotImplementedError

    def generate_session_key(self):
        """
        Generate 16 digit session Key
        """
        return ''.join(random.choice(string.digits + string.letters) for _ in range(16))

    def base64url_rsa_encrypt(self, value, public_key):
        """
        Encrypt th URL with rsa
        """
        rsakey = RSA.importKey(public_key)
        cipher = PKCS1_OAEP.new(rsakey)

        # encrypt, IMPORTANT: read about padding modes (RSA.pkcs1_padding)
        encrypted_msg = cipher.encrypt(value)

        if encrypted_msg:
            b64 = encrypted_msg.encode('base64')
            b64 = re.sub('(/)', '_', b64)
            b64 = re.sub('(\+)', '-', b64)
            b64 = re.sub('(=)', '.', b64)
            return b64
        else:
            return AlignetError('RSA Ciphering could not be executed')

    def base64url_rsa_decrypt(self, value, privatekey):
        raise NotImplementedError

    def base64url_symmetric_cipher(self, data, key, vector):
        if len(vector) != 16:
            raise AlignetError('Initialization Vector must have 16 hexadecimal characters')
            return None

        if len(key) != 16:
            raise AlignetError("Simetric Key doesn't have length of 16")
            return None

        #Convert the vector to binary
        binvector = binascii.unhexlify(vector)

        if not binvector:
            raise AlignetError('Initialization Vector is not valid, must contain only hexadecimal characters')
            return None

        #Add 8 first bytes of key at the end of it
        key += key[0:8]

        block = DES3.block_size
        text = data
        padding = block - (len(text) % block)

        text += chr(padding) * padding

        des3 = DES3.new(key, DES3.MODE_CBC, binvector)
        crypttext = base64.b64encode(des3.encrypt(text))

        crypttext = re.sub('(/)', '_', crypttext)
        crypttext = re.sub('(\+)', '-', crypttext)
        crypttext = re.sub('(=)', '.', crypttext)

        return crypttext

    def base64url_symmetric_decipher(self, data, key, vector):

        #Convert the vector to binary
        binvector = binascii.unhexlify(vector)

        #Add 8 first bytes of key at the end of it
        key += key[0:8]

        pas = re.sub('_', '/', data)
        pas = re.sub('-', '+', pas)
        pas = re.sub('\.', '=', pas)

        crypttext = base64.b64decode(pas)

        des3 = DES3.new(key, DES3.MODE_CBC, binvector)
        crypttext2 = des3.decrypt(crypttext)

        packing = ord(crypttext2[len(crypttext2) - 1])
        if packing and packing < DES3.block_size:
            p = len(crypttext2) - 1
            while p <= len(crypttext2) - packing:
                if ord(crypttext2[p] != packing):
                    packing = 0

        return crypttext2[0: len(crypttext2) - packing]

    def base64url_digital_generate(self, data, privatekey):
        raise NotImplementedError

    def base64url_digital_verify(self, sata, signature, publickey):
        raise NotImplementedError

    def parse_xml(self, xml):
        raise NotImplementedError


if __name__ == "__main__":
    data = "Dairon Medina"
    vector = "1234567891011111";
    key = "1234567891011112"
    al = Alignet()
    ci = al.base64url_symmetric_cipher(data, key, vector)
    print ci
    de = al.base64url_symmetric_decipher(ci, key, vector)
    print de

    send = {
        'purchaseCurrencyCode': 'USD',
        'billingEMail': 'dairon.medina@gmail.com',
        'billingPhone': '0987612278'
    }

    print al.create_xml(send)

    key = """
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDMk8iGBH93T4WGSlCl8tQGSOQV
giOnHUO5SK8SMao/9VpgQncOJW7h6EooEZo9EdPSt+Ezn/3ausbNwoA7+Y/mNOcD
2ThSSgZ8FRk9sUq6/pq0JiK0/stQfyYLldeW0NGg99RDf8AKQ3/FzjRAJCdwgOx0
NqbMDDdUFhFNdVNg0wIDAQAB
"""
    key = base64.b64decode(key)
    print al.base64url_rsa_encrypt(data, key)

