import httplib2
import json
import time
import datetime

t0 = time.time()
h = httplib2.Http()
for i in range(1000):
    data={"published": i,"actor": {"url": "http://example.org/martin","objectType" : "person","id": "victor","image": {"url": "http://example.org/martin/image","width": 250,"height": 250}, "displayName": "Victor Fernandez de Alba"},"verb": "post","object" : {"url": "http://example.org/blog/2011/02/entry","id": "tag:example.org,2011:abc123/xyz"},"target" : {"url": "http://example.org/blog/","objectType": "blog","id": "tag:example.org,2011:abc123","displayName": "Martin's Blog"}}
    data_json = json.dumps(data)
    h.request("http://localhost:6543/activity",
              "POST",
              data_json,
              headers={'Content-Type': 'application/json'})
print "%.3f segons" % (time.time()-t0)
