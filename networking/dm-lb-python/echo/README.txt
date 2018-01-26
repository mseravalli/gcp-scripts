## Echo 
"The simplest web app on earth"...
## Build
    $ python setup.py sdist
    $ ls -l dist
    total 8
    -rw-r--r--  1 mwallman  eng  1719 Aug 19 15:30 echo-0.0.1.tar.gz
    
## Serve from GCS
   
    $ gsutil -h 'Content-Type: application/gzip' -h 'Cache-Control:private' cp
-a public-read echo-0.0.1.tar.gz gs://<bucket>
## Install
    $ pip install http://storage.googleapis.com/<bucket>/echo-0.0.1.tar.gz
## Run 
    
    $ gunicorn -b 0.0.0.0:80 -w 4 echo:app 

