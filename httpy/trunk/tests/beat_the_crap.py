#! /usr/bin/env python
import urllib
import time
import threading
from pprint import pprint
import sys
import os
import Queue

class crap_beater:
    def __init__(self,threads,hits,repeats,test_num,test_total):
        self.threads = threads
        self.hits = hits
        self.repeats=repeats
        self.test_num = test_num
        self.test_total = test_total

        self.results = {
        'hits':0,
        'errors': 0,
        'failures': 0, 
        'successes': 0,}
        self.errors={}
        self.hit_queue=Queue.Queue()
        for i in range(self.hits):
            self.hit_queue.put(1)

    def run(self):
        print '\nhitting server %s times using %s concurrent threads (test %s of %s)'%(self.hits,self.threads,self.test_num,self.test_total)
        threads = []
        start=time.time()
        for i in range(self.threads):
            thread = threading.Thread(target=self.hit)
            threads.append(thread)
            thread.start()
        last_percent=0
        repeated_percents=0
        while self.results['hits']<self.hits and threading.activeCount()>1:
            percent = (float(self.results['hits'])/self.hits)*100
            sys.stdout.write('%d%% '%percent)
            sys.stdout.flush()
            if percent!=last_percent:
                last_percent=percent
                repeated_percents=0
            else:
                repeated_percents+=1
            if repeated_percents>self.repeats:
                print '\nhung up with %s living threads'%threading.activeCount()
                self.elapsed=time.time()-start
                return self.wrapup()
                os.kill(os.getpid(),9)
            time.sleep(1)
        else:
            sys.stdout.write('100%')
            print
        for thread in threads:
            thread.join()
        self.elapsed=time.time()-start
        return self.wrapup()
    
    
    def hit(self):
        while not self.hit_queue.empty():
            hits = self.hit_queue.get()
            for i in range(hits):
                self.results['hits']+=1
                try:
                    response = urllib.urlopen('http://localhost:9999')
                    success=True
                    if 0:
                        headers = str(response.headers).strip().replace('\r','')
                        body = response.read().strip().replace('\r','')
                        success = (headers==HEADERS and body==BODY)
                    if success:
                        self.results['successes']+=1
                    else:
                        self.results['failures']+=1
                except:
                    self.results['errors']+=1
                    err_type, err_value,err_traceback=[str(thing) for thing in sys.exc_info()]
                    key = '%s: %s'%(err_type,err_value)
                    if key in self.errors:
                        self.errors[key]+=1
                    else:
                        self.errors[key]=1
                    #break
                
    def wrapup(self):
        print 'finished in %.2f seconds'%self.elapsed
        return (self.threads,self.hits,self.results,self.errors,self.elapsed)

def pretty_results(allresults):
    print'\nRESULTS!\n'
    all_errors={}
    colwidth=12
    table_rows = []
    graph_rows = []
    row=['threads'
        ,'hits'
        ,'successes'
        ,'errors'
        ,'reliability'
        ,'req/sec']
    table_rows.append(row)
    row = ['-'*colwidth for i in range(len(row))]
    table_rows.append(row)
    for threads, hits, results,errors,elapsed in allresults:
        all_errors.update(errors)
        reliability='%d%%'%(float(results['successes'])*100/results['hits'])
        raw_rate = float(results['successes'])/elapsed
        rate = ('%.2f'%(raw_rate)).rjust(6)
        graph_rows.append([str(threads).rjust(8),'#'*int(raw_rate)])
        row=[str(threads).rjust(4)
            ,str(results['hits']).rjust(5)
            ,str(results['successes']).rjust(5)
            ,str(results['errors']).rjust(3)
            ,reliability
            ,rate]
        table_rows.append(row)
    print
    for columns in table_rows:
        pretty_cols = [col.center(colwidth) for col in columns]
        print '|'.join(pretty_cols)
    print
    print ' threads | requests/sec'
    print '-'*107
    for row in graph_rows:
        num,line = row
        print num,'|',line
    print 
    pprint(all_errors)
    
def SLAMIT(thread_opts,hits,repeats,rest):
    configs = []
    results = []
    for thread_opt in thread_opts:
        configs.append([thread_opt,hits,repeats])
    i=0
    j=len(configs)
    for config in configs:
        i+=1
        config.extend([i,j])
        cb = crap_beater(*config)
        results.append(cb.run())
        if i<j:
            print 'letting the server rest for %s seconds ;-)'%rest
            time.sleep(rest)
    pretty_results(results)
if __name__=='__main__':
    thread_opts=[280]
    #thread_opts=[300,320,340,360,380,400]
    hits=30000
    repeats=10
    rest =30
    SLAMIT(thread_opts,hits,repeats,rest)