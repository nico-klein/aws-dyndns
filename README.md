# aws_dyndns
It' a very simple custom implementation of dynamic dns as lambda function on aws.
Security is only to check the given password of the caller - not more.
It works with well with my fritzbox. I have a domain with subdomains hosted on aws.

The lambda service does the following things:
* check the given password and (sub)domain with the values in the config file
* take ipv4 and ip6 adresses from caller
* update ipv4 and ipv6 adresses of (sub)domain in route53
* write log entry in history.json

## what you need:
### route 53
* for each dyn dns one (sub)domain with entries for
  * ipv4 (A)
  * ipv6 (AAAA)
* one (sub)domain for the lambda service itself

### s3 
* bucket for storing the config file (config.json) and logfile (history.json)
* config.json with (sub)domain(s) and passwords

### lambda 
* the python file file with the functionality
* policy with the rights (sample is in the repo)

### api-gateway
* one entry with HTTP GET connected to LAMBDA_PROXY




