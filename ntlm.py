# -*- coding: cp936 -*-
import sys, httplib, base64, string
import urllib2
import win32api
import sspi 
import pywintypes
import socket
import re
import random
import cookielib
import Image


class WindoewNtlmMessageGenerator:
    def __init__(self,user=None):
       import win32api,sspi
       if not user:
           user = win32api.GetUserName()
       self.sspi_client = sspi.ClientAuth("NTLM",user)

    def create_auth_req(self):
       import pywintypes
       output_buffer = None
       error_msg = None
       try:
           error_msg, output_buffer = self.sspi_client.authorize(None)             
       except pywintypes.error:           
            return None
       auth_req = output_buffer[0].Buffer
       auth_req = base64.b64encode(auth_req)
       return auth_req

    def create_challenge_response(self,challenge):
      output_buffer = None
      input_buffer = challenge
      error_msg = None
      try:
          error_msg, output_buffer = self.sspi_client.authorize(input_buffer)
      except pywintypes.error:
          return None
      response_msg = output_buffer[0].Buffer        
      response_msg = base64.b64encode(response_msg) 
      return response_msg

