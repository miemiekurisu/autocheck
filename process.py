import ntlm
from ntlm import WindoewNtlmMessageGenerator
import img
import sys, httplib, base64, string
import urllib2
import win32api
import sspi 
import pywintypes
import socket
import re
import random
import cookielib
import pytesseract
import Image
import time
import logging
import logging.handlers
import ConfigParser
from apscheduler.schedulers.background import BackgroundScheduler
import os

CHECK_HOST ='hr.tpis.tpaic.com'
PIC_URL='/hr/hrDomain/empSign.do'
CHECK_IN_URL='/hr/hrDomain/empSignIn.do?'
CHECK_OUT_URL='/hr/hrDomain/empSignOut.do?'
USER=win32api.GetUserName()
CHECK_STR='loginname=%s&verifyCode=%s&browserType=safari&MACAddress=&IPAddress=&sDNSName=&radom=%s'
UN_AUTHENTICATE=401
CHECKDAY='1-5'
CHECKINTIME=['8','30']
CHECKOUTTIME=['17','50']

fm,df="%(asctime)s  %(levelname)s - %(message)s","%Y-%m-%d %H:%M:%S"
logging.basicConfig(format=fm,datefmt=df,filename='check.log',level=logging.INFO,filemod='w')

def loadconfig():
    def __init__(self):
        logging.info('Loading Config')
        config.readfp(open('config.cfg'))
        CHECK_HOST = config.get('Main CFG','CHECK_HOST')
        PIC_URL=config.get('Main CFG','PIC_URL')
        CHECK_IN_URL=config.get('Main CFG','CHECK_IN_URL')
        CHECK_OUT_URL=config.get('Main CFG','CHECK_OUT_URL')
        CHECK_STR=config.get('Main CFG','CHECK_STR')
        UN_AUTHENTICATE=config.getint('Main CFG','UN_AUTHENTICATE')
        CHECKDAY=config.get('Main CFG','CHECKDAY')
        CHECKINTIME=config.get('Main CFG','CHECKINTIME')
        CHECKOUTTIME=config.get('Main CFG','CHECKOUTTIME')
        logging.info('Configration Loaded')
    pass
        

def checktime():
    today = time.strftime('%Y%m%d',time.localtime(time.time()))
    todaynowtime = time.localtime(time.time())
    checkintime=time.strptime(today+'0850','%Y%m%d%H%M')
    checkouttime=time.strptime(today+'1735','%Y%m%d%H%M')

    if todaynowtime <= checkintime:
        inot='in'
    elif todaynowtime >= checkouttime:
        inot='out'
    return inot

def check(ck):
    ntlm_gen = WindoewNtlmMessageGenerator()
    auth_req_msg = ntlm_gen.create_auth_req()
    conn = httplib.HTTPConnection(CHECK_HOST)
    conn.putrequest("GET",PIC_URL)
    conn.putheader("Content-type", "text/html;charset=GBK")
    conn.putheader("Connection", "Keep-Alive")
    conn.putheader('Authorization', 'NTLM'+' '+auth_req_msg) 
    conn.endheaders()
    res=conn.getresponse()
    res.read()
    challenge = res.msg.get('WWW-Authenticate')
    challenge_dec = base64.b64decode(challenge.split()[1])
    msg3 = ntlm_gen.create_challenge_response(challenge_dec)
    fakecookie = res.msg.dict['set-cookie'].split(';')[0]
    if fakecookie=="" or len(fakecookie)==0:
        raise Exception("Can't get fakecookie!")
    conn.putrequest("GET", PIC_URL)
    conn.putheader("Content-type", "text/html;charset=GBK")
    conn.putheader("Connection", "Keep-Alive")
    conn.putheader("Cookie",fakecookie)
    conn.putheader('Authorization', 'NTLM'+' '+msg3)
    conn.endheaders()
    resp = conn.getresponse()
    res=resp.read()

    #Get picture URL
    pat =  re.compile(r'\/hr\/servlet.*\d+')
    picreq = re.search(pat,res).group()
    conn = httplib.HTTPConnection(CHECK_HOST)
    conn.putrequest("GET", picreq)
    conn.putheader("Accept","image/webp,*/*;q=0.8")
    conn.putheader("Content-type", "text/html;charset=GBK")
    conn.putheader("Connection", "Keep-Alive")
    conn.putheader("Cookie",fakecookie)
    conn.endheaders()
    res = conn.getresponse()
    #write picture
    g=open('pic.jpg','wb')
    g.write(res.read())
    g.close()
    

    code = img.readimage('pic.jpg')
    #ck=checktime()

    if code=='':
        return -1,-1
    if ck=='in':
        logging.info('Checkin')
        requrl = CHECK_IN_URL+CHECK_STR % (USER,code,str(random.random()*100))
    elif ck=='out':
        logging.info('Checkout')
        requrl = CHECK_OUT_URL+CHECK_STR % (USER,code,str(random.random()*100))
    else:
        logging.info('Othertime, need not check')
        return 99,99
    conn.putrequest("GET", requrl)
    conn.putheader("x-requested-with","XMLHttpRequest")
    conn.putheader("Content-type", "text/html;charset=GBK")
    conn.putheader("Accept","application/json, text/javascript, */*")
    conn.putheader("Connection", "keep-alive")
    conn.putheader("Cookie",fakecookie)
    conn.putheader('Authorization', 'NTLM'+' '+msg3) 
    conn.endheaders()
    res=conn.getresponse()
    #{"result":"success"}
    exec("ifcussess="+res.read())
    checkstat= -1
    if ifcussess['result']=='success':
        checkstat= 0
    return res.status,checkstat
    

def maincheck():
    
    logging.info('Start Check')
    stat = -1
    checkstat = -1

    while stat!=httplib.OK or checkstat!=0:
        ck=checktime()
        #print ck
        stat,checkstat = check(ck)
        if stat==99 and checkstat==99:
            break
        logging.info('stat=%s, checkstat=%s'%(stat,checkstat))
    if  stat==httplib.OK and checkstat==0:
        logging.info('Check Success')
    logging.info('End Check')

if __name__ == '__main__':
    loadconfig()
    scheduler = BackgroundScheduler()
    scheduler.add_job(maincheck,'cron',day_of_week=CHECKDAY,hour=CHECKINTIME[0],minute=CHECKINTIME[1])
    scheduler.add_job(maincheck,'cron',day_of_week=CHECKDAY,hour=CHECKOUTTIME[0],minute=CHECKOUTTIME[1])
    scheduler.start()
    print('Please Press Ctrl+{0} to exit'.format('C' if os.name=='nt' else 'C'))

    try:
        while True:
            time.sleep(2)
    except (KeyboardInterrupt,SystemExit):
        scheduler.shutdown()
