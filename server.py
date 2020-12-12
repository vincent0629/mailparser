# -*- coding: utf-8 -*-

import asyncore
import email
import json
import smtpd
from email.header import decode_header

class SMTPServer(smtpd.SMTPServer):
  def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
    mail = {}
    mail['envelope'] = {
      'from': mailfrom,
      'recipients': rcpttos
    }
    mail['body'] = self.parse(email.message_from_bytes(data))
    print(json.dumps(mail, indent=2, ensure_ascii=False))

  def parse(self, msg):
    headers = {}
    for (key, value) in msg.items():
      headers[key] = self.decodeHeader(value)
    payloads = []
    if msg.is_multipart():
      try:
        i = 0
        while True:
          payloads.append(self.parse(msg.get_payload(i)))
          i += 1
      except IndexError:
        pass
    elif msg.get_content_maintype() == 'text':
      payload = msg.get_payload(None, True)
      if isinstance(payload, bytes):
        payload = payload.decode(msg.get_content_charset())
      payloads.append(payload)
    else:
      payloads.append(msg.get_payload())
    return {
      'headers': headers,
      'payloads': payloads
    }

  def decodeHeader(self, header):
    values = []
    for pair in decode_header(header):
      if pair[1]:
        value = pair[0].decode(pair[1])
      elif isinstance(pair[0], bytes):
        value = pair[0].decode()
      else:
        value = pair[0]
      values.append(value)
    return ''.join(values)

server = SMTPServer(('0.0.0.0', 1025), None)
asyncore.loop()
