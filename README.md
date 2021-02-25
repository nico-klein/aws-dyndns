# aws_dyndns
easy custom dyndns as lambda on aws (works with fritzbox)

* a lambda service is called
* check the given password and (sub)domain with values in config file
* update ipv4 and ipv6 in route53
* write log entry in history.json


### s3 
* bucket for config file (config.json) and logfile (history.json)
* config.json with (sub)domain(s) and passwords

## lambda 
* the python file file with the functionality

### api-gateway
one entry with GET connected to LAMBDA_PROXY

### route 53
* for each dyn-dns one (sub)domain with entries for
  * ipv4 A
  * ipv6 AAAA
* one (sub)domain for lambda service


