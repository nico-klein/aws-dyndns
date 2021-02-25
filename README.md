# aws_dyndns
It' a simple very simple custom implementation of dynamic dns as lambda function on aws.
It works with well my fritzbox. I have a domain ad subdomains hosted on aws.

The lambda service does the following things:
* checks the given password and (sub)domain with the values in the config file
* takes ipv4 and ip6 adresses from caller
* updates ipv4 and ipv6 adresses of (sub)domain in route53
* writes log entry in history.json

## what you need:
### route 53
* for each dyn-dns one (sub)domain with entries for
  * ipv4 A
  * ipv6 AAAA
* one (sub)domain for lambda service

### s3 
* bucket for config file (config.json) and logfile (history.json)
* config.json with (sub)domain(s) and passwords

### lambda 
* the python file file with the functionality

### api-gateway
* one entry with GET connected to LAMBDA_PROXY




