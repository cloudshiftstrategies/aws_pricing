# aws_pricing project

## Overview

This is a tool designed to make it easier to look up AWS pricing information. The tool was built pretty quickly and as a result may contain errors. 

## Command Line Examples

To get EC2 Pricing for a t2.micro Linux instance running in us-east-1:

```bash
./aws_pricing.py pricing -s AmazonEC2 -r us-east-1 -o RunInstances -i t2.micro
Description: $0.0116 per On Demand Linux t2.micro Instance Hour
OperatingSystem: Linux
CPU: (1)Up to 3.3 GHz Intel Xeon Family
Memory: 1 GiB
Network Performance: Low to Moderate
Storage: EBS only
OD Hourly Price: $0.0116
RI Hourly Price: $0.0072
RI Upfront Price: $0.00
RI Hourly Discount: 38.0%
```

To get EC2 pricing for a c5.large RHEL instance running in us-east-1 with json output:
```bash
./aws_pricing.py pricing -s AmazonEC2 -r us-east-1 -o RunInstances:0010 -i c5.large  --json-out
{
  "attributes": {
    "service": "AmazonEC2",
    "instanceType": "c5.large",
    "operation": "RunInstances:0010",
    "location": "US East (N. Virginia)",
    "region": "us-east-1",
    "OfferingClass": "standard",
    "PurchaseOption": "No Upfront",
    "LeaseContractLength": "1yr",
    "enhancedNetworkingSupported": "Yes",
    "memory": "4 GiB",
    "dedicatedEbsThroughput": "Upto 2250 Mbps",
    "vcpu": "2",
    "capacitystatus": "Used",
    "locationType": "AWS Region",
    "storage": "EBS only",
    "instanceFamily": "Compute optimized",
    "operatingSystem": "RHEL",
    "physicalProcessor": "Intel Xeon Platinum 8124M",
    "clockSpeed": "3.0 Ghz",
    "ecu": "9",
    "networkPerformance": "Up to 10 Gigabit",
    "servicename": "Amazon Elastic Compute Cloud",
    "instancesku": "BWKDS9539ZWVQSVQ",
    "tenancy": "Host",
    "usagetype": "HostBoxUsage:c5.large",
    "normalizationSizeFactor": "4",
    "processorFeatures": "Intel AVX, Intel AVX2, Intel AVX512, Intel Turbo",
    "servicecode": "AmazonEC2",
    "licenseModel": "No License required",
    "currentGeneration": "Yes",
    "preInstalledSw": "NA",
    "processorArchitecture": "64-bit"
  },
  "OnDemand": {
    "unit": "Hrs",
    "description": "$0.145 per On Demand RHEL c5.large Instance Hour",
    "hr_price": 0.145
  },
  "Reserved": {
    "hr_price": 0.119,
    "description": "Red Hat Enterprise Linux (Amazon VPC), c5.large reserved instance applied",
    "discount": 18.0
  }
}
```

To see a list of EC2 operations translated to operating sustems:
```bash
./aws_pricing.py operations AmazonEC2
AmazonEC2 - RunInstances:0002 : Windows
AmazonEC2 - RunInstances:0004 : Linux with SQL Std
AmazonEC2 - RunInstances:0006 : Windows with SQL Std
AmazonEC2 - RunInstances:000g : SUSE
AmazonEC2 - RunInstances:0010 : RHEL
AmazonEC2 - RunInstances:0100 : Linux with SQL Server Enterprise
AmazonEC2 - RunInstances:0102 : Windows with SQL Server Enterprise
AmazonEC2 - RunInstances:0200 : Linux with SQL Web
AmazonEC2 - RunInstances:0202 : Windows with SQL Web
AmazonEC2 - RunInstances:0800 : Windows BYOL
AmazonEC2 - RunInstances : Linux
```

To check the price of a 3yr, all upfront db.r4.large RI for Aurora us-west-2
```bash
# First determine the operation name for Aurora
./aws_pricing.py operations AmazonRDS | grep Aurora
AmazonRDS - CreateDBInstance:0016 : Amazon Aurora
AmazonRDS - CreateDBInstance:0021 : Amazon Aurora PostgreSQL

# Then run the pricing check for operation: CreateDBInstance:0016
./aws_pricing.py pricing -s AmazonRDS -o CreateDBInstance:0016 -r us-west-2 -i db.r4.large -L 3yr -P "All Upfront"
Description: $0.29 per RDS db.r4.large instance hour (or partial hour) running Amazon Aurora
DB Engine: Aurora MySQL
CPU: (2)2.3 GHz Intel Xeon E5-2686 v4 (Broadwell)
Memory: 15.25 GiB
Network Performance: Up to 10 Gigabit
EBS Performance: 400 Mbps
OD Hourly Price: $0.29
RI Hourly Price: $0.0
RI Upfront Price: $2657.0
RI Hourly Discount: 100.0%
RI Payback Period (mos): 12.2
```

## Module examples
This library is also designed to be used as a module in your python apps

```python
>>> from aws_pricing import pricing
>>> pricing.get_services()[:5]
['AWSAppSync', 'AWSBudgets', 'AWSCertificateManager', 'AWSCloudTrail', 'AWSCodeCommit']

>>> pricing.get_pricing(service="AmazonEC2", instanceType="t2.micro", operation="RunInstances:0002", region="us-west-2")
{'attributes': {'service': 'AmazonEC2', 'instanceType': 't2.micro', 'operation': 'RunInstances:0002', 'location': 'US West (Oregon)', 'region': 'us-west-2', 'OfferingClass': 'standard', 'PurchaseOption': 'No Upfront', 'LeaseContractLength': '1yr'}, 'OnDemand': {'unit': 'Hrs', 'description': '$0.0162 per On Demand Windows t2.micro Instance Hour', 'hr_price': 0.0162}, 'Reserved': {'hr_price': 0.0118, 'description': 'Windows (Amazon VPC), t2.micro reserved instance applied', 'discount': 27.0}}

```

## Requirements
0. an AWS account with API credentials
1. git (to download this repository)
1. python3 or greater
2. `boto3` pip module installed
3. `begins` pip module installed

## Installation on Linux/mac

1. Clone this repo
```
git clone https://github.com/cloudshiftstrategies/aws_pricing
```

2. Create a virtual environment and install the libraries
```bash
cd aws_pricing
python3 -m venv ./venv
source ./venv/bin/activate
pip install -r requirements.txt
```

3. Setup your AWS credentials 
Either [set AWS API environment variables](https://docs.aws.amazon.com/cli/latest/userguide/cli-environment.html)
or
[Use credentials file](https://docs.aws.amazon.com/cli/latest/userguide/cli-multiple-profiles.html)


## CLI Usage
There is extensive help on the commands and subcommands with -h
```bash
./aws_pricing.py -h

usage: aws_pricing.py [-h] [-v | -q]
                  [--loglvl {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                  [--logfile LOGFILE] [--logfmt LOGFMT]
                  {attr_vals,attrs,loc_to_reg,operations,pricing,regions,services}
                  ...

Extracts pricing data from AWS

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Increse logging output
  -q, --quiet           Decrease logging output

Available subcommands:
  {attr_vals,attrs,loc_to_reg,operations,pricing,regions,services}
    attr_vals           gets list values for a service/attribute
    attrs               gets a list of pricing attributes for an AWS service
    loc_to_reg          converts aws region name to location and vice versa
    operations          gets the operating system name for an AWS operation
    pricing             gets AWS on demand and RI pricing for a resouce
    regions             gets a list of AWS regions
    services            gets a list of AWS services

logging:
  Detailed control of logging output

  --loglvl {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Set explicit log level
  --logfile LOGFILE     Ouput log messages to file
  --logfmt LOGFMT       Log message format
```
