#!/usr/bin/env python

def PARTS(newline='\r\n'):
    IE_CRAP="\r\n\n\r"
    LINE = "POST http://netloc/path;parameters?query#fragment HTTP/1.1"+newline
    LINE2 = "GET / HTTP/1.1"+newline
    HEADERS = newline.join([
          "Host: josemaria:5370"
        , "User-Agent: Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7.10) Gecko/20050716 Firefox/1.0.6"
        , "Accept: text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5"
        , "Accept-Language: en-us,en;q=0.7,ar;q=0.3"
        , "Accept-Encoding: gzip,deflate"
        , "Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.7"
        , "Keep-Alive: 300"
        , "Connection: keep-alive"
        , "Referer: http://www.zetadev.com/tmp/test.html"
        , "Content-Type: application/x-www-form-urlencoded"
        , "Content-Length: 8"
        , newline
         ])
    HEADERS2 = newline.join([
          "Host: josemaria:5370"
        , "User-Agent: Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7.10) Gecko/20050716 Firefox/1.0.6"
        , "Accept: text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5"
        , "Accept-Language: en-us,en;q=0.7,ar;q=0.3"
        , "Accept-Encoding: gzip,deflate"
        , "Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.7"
        , "Keep-Alive: 300"
        , "Connection: keep-alive"
        , "Referer: http://www.zetadev.com/tmp/test.html"
        , newline
         ])
    BODY = "foo=test"
    POST = IE_CRAP+LINE+HEADERS+BODY
    GET = IE_CRAP+LINE2+HEADERS2
    return (IE_CRAP,LINE,LINE2,HEADERS,HEADERS2,BODY,POST,GET)
