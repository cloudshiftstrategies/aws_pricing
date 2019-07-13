#!/usr/bin/env python3
import boto3, json, begin, logging

region_name='us-east-1'
logging.getLogger('botocore').setLevel(logging.WARNING)


def get_services():
    """ Return a list of AWS service names (i.e. ['AmazonEC2', 'AmazonRDS']
    Called as a module

    Returns:
        list: alist of AWS Service names
    """
    pricing = boto3.client('pricing', region_name=region_name)
    response = pricing.describe_services()
    services = []
    for service in response['Services']:
        services.append(service['ServiceCode'])
    return services

@begin.subcommand()
def services():
    """Print a list of AWS service names
    Called from CLI

    Returns:
        bool: True
    """
    for service in get_services():
        print(service)

def get_attrs(service):
    """ Return a list of pricing attribute names for an AWS service
    Called as a module

    Args:
        service (str): a string with a valid AWS Service Name
    Returns:
        list: a list of pricing attribute names for the service
    """
    pricing = boto3.client('pricing', region_name=region_name)
    response = pricing.describe_services(ServiceCode=service)
    return response['Services'][0]['AttributeNames']
@begin.subcommand()
def attrs(service):
    """Print a list of pricing attributes for an AWS service
    Called from CLI

    Args:
        service (str): a string with valid AWS Service Name
    Returns:
        bool: True
    """
    for attr in get_attrs(service):
        print(attr)

def get_attr_vals(service, attr):
    """ Return a list of pricing attribute values
    Called as a module

    Args:
        service (str): a string with a valid AWS service name
        att (str): a string with a valid AWS Pricing attribute name for service
    Returns:
        list: a list of attribute values for AWS Service / Pricing Attribute
    """
    pricing = boto3.client('pricing', region_name=region_name)
    response = pricing.get_attribute_values(ServiceCode=service, AttributeName=attr)
    vals = []
    for val in response['AttributeValues']:
        vals.append(val['Value'])
    return vals
@begin.subcommand()
def attr_vals(service, attr):
    """Print a list values for a service/attribute
    Called from CLI

    Args:
        service (str): a string with a valid AWS service name
        att (str): a string with a valid AWS Pricing attribute name for service
    Returns:
        bool: True
    """
    for val in get_attr_vals(service, attr):
        print(val)

def get_regions():
    """ Return a list of aws region names
    Called as a module

    Return:
        list: a list of AWS region name strings
    """
    ec2 = boto3.client('ec2', region_name=region_name)
    response = ec2.describe_regions()
    regions = []
    for region in response['Regions']:
        regions.append(region['RegionName'])
    return regions
@begin.subcommand()
def regions():
    """ Print a list of AWS regions
    Called from CLI

    Return:
        bool: True
    """
    for region in get_regions():
        print(region)

@begin.subcommand()
def loc_to_reg(location=None, region=None):
    """ Converts aws region name to location and vice versa. Provide location or region
    Called as a module

    Args (provide either location or region):
        location (str): AWS location name ex. 'US East (N. Virginia)'. Default = None
        region (str): Aws region name ex. 'us-east-1'. Default = None
    Return:
        str: the corresponding region or location string name

    """
    map = {
        "AWS GovCloud (US)" : "us-gov-west-1",
        "Asia Pacific (Mumbai)" : "ap-south-1",
        "Asia Pacific (Osaka-Local)" : "ap-northeast-3",
        "Asia Pacific (Seoul)" : "ap-northeast-2",
        "Asia Pacific (Singapore)" : "ap-southeast-1",
        "Asia Pacific (Sydney)" : "ap-southeast-2",
        "Asia Pacific (Tokyo)" : "ap-northeast-1",
        "Canada (Central)" : "ca-central-1",
        "EU (Frankfurt)" : "eu-central-1",
        "EU (Ireland)" : "eu-west-1",
        "EU (London)" : "eu-west-2",
        "EU (Paris)" : "eu-west-3",
        "South America (Sao Paulo)" : "sa-east-1",
        "US East (N. Virginia)" : "us-east-1",
        "US East (Ohio)" : "us-east-2",
        "US West (N. California)" : "us-west-1",
        "US West (Oregon)" : "us-west-2"
    }
    if location:
        if location in map.keys():
            return map[location]
        else:
            raise Exception(f"location: {location} not valid. Must be in {map.keys()}")
    elif region:
        for location in map.keys():
            if map[location] == region:
                return location
        Exception(f"region: {region} not valid. Must be in {map}")
    else:
        Exception(f"must provide a location or region from {map}")

def get_operation_description(service, operation):
    """ Return the description of an operation for a service
    Called as a module

    Args:
        service (str): Valid AWS Service name
        operation (str): Valid AWS Operation name
    Return:
        str : the description string for a Service / Operation
    """
    pricing = boto3.client('pricing', region_name=region_name)
    location = loc_to_reg(region=region_name)
    instanceType = 't2.micro'
    response = pricing.get_products(
         ServiceCode = service,
         Filters = [
             {'Type' :'TERM_MATCH', 'Field':'operation', 'Value': operation},
             {'Type' :'TERM_MATCH', 'Field':'location',  'Value': location}
         ],
         MaxResults=100
    )
    if len(response['PriceList']) == 0:
            raise Exception("query returned zero results")
    for price in response['PriceList']:
        jprice = json.loads(price)
        for key in jprice['terms']['OnDemand'].keys():
            for key2 in jprice['terms']['OnDemand'][key]['priceDimensions'].keys():
                description = jprice['terms']['OnDemand'][key]['priceDimensions'][key2]['description']
        if service == 'AmazonEC2' and 'On Demand' in description:
            break
    if service == 'AmazonRDS':
        if 'running' in description:
            description = description.split('running')[1].strip()
    elif service == 'AmazonEC2':
        if 'On Demand' in description:
            description = description.split('On Demand')[1].split('.')[0][:-3].strip()
    return description
@begin.subcommand()
def operations(service, operation=None, json_out=False):
    """Prints the operating system name for AmazonEC2 or Amazon RDS operation(s)
    Called from CLI

    Arguments:
        service (str): Valid AWS Service Name. ex. AmazonEC2
        operation (str): AWS operation name. default = None (returns all operations). ex. RunInstances
        json_out (bool): True/False. If true, printed output is json format.
    Return:
        bool: True
    """
    if operation == None:
        operations = []
        ops = get_attr_vals(service, 'operation')
        for op in ops:
            if 'RunInstances' in op or 'CreateDBInstance:' in op:
                operations.append(op)
    elif type(operation) == 'str':
        operations = [operation]
    elif type(operation) == 'list':
        operations = operation
    output = {}
    for operation in operations:
        result = get_operation_description(service, operation)
        output[operation] = result
        if json_out == False:
            print(f"{service} - {operation} : {result}")
    if json_out == True:
        print(json.dumps(output, indent=2))

def get_pricing(service=None, instanceType=None, operation=None, region=None, \
        LeaseContractLength='1yr', OfferingClass='standard', PurchaseOption='No Upfront'):
    """ Returns a dict of AWS pricing values for a set of parms
    Called as a module

    Args:
        service (str) : AWS service name. options 'AmazonEC2'|'AmazonRDS.
        instanceType (str) : Instance Type. e.x. 't2.micro' | 'db.t2.micro'
        operation (str) :  Operation. e.x. 'RunInstances' | 'RunINstances:0002' | 'CreateDBInstance:0014'
        region (str) : AWS region name. e.x 'us-east-1'
        LeaseContractLength (str) : RI contract length. default = '1yr'. options '1yr'|'3yr'
        OfferingClass (str) : RI offering class. default = 'standard'. options: 'standard'|'convertible'
        PurchaseOption (str) : RI purchase option. default = 'No Upfront'. options: 'All Upfront'|'Partial Upfront'|'No Upfront'
    Return
        dict: dictionary of pricing parameters
    """

    services = ['AmazonEC2', 'AmazonRDS']
    if service not in services:
        raise Exception(f"service: '{service}' invalid. Must be one of {services}")

    #instanceTypes = get_attr_vals(service, 'InstanceType')
    #if instanceType not in instanceTypes:
    #    raise Exception(f"instanceType: '{instanceType}' invalid. Must be one of {instanceTypes}")

    operations = get_attr_vals(service, 'operation')
    if operation not in operations:
        raise Exception(f"operation: '{operation}' invalid. Must be one of {operations}")

    regions = get_regions()
    if region not in regions:
        raise Exception(f"region: '{region}' invalid. Must be one of {regions}")
    location = loc_to_reg(region=region)

    LeaseContractLengths = ['1yr', '3yr']
    if LeaseContractLength not in LeaseContractLengths:
        raise Exception(f"LeaseContractLength: '{LeaseContractLengths}' invalid. Must be one of {LeaseContractLengths}")

    OfferingClasses = ['standard', 'convertible']
    if OfferingClass not in OfferingClasses:
        raise Exception(f"OfferingClass: '{OfferingClass}' invalid. Must be one of {OfferingClasses}")

    PurchaseOptions = ['All Upfront', 'Partial Upfront', 'No Upfront']
    if PurchaseOption not in PurchaseOptions:
        raise Exception(f"PurchaseOption: '{PurchaseOption}' invalid. Must be one of {PurchaseOptions}")

    if service == 'AmazonRDS' and OfferingClass != 'standard':
        raise Exception(f"service: {service} only supports OfferingClass: 'standard'. Not '{OfferingClass}'")

    pricing = boto3.client('pricing', region_name=region_name)
    response = pricing.get_products(
         ServiceCode = service,
         Filters = [
             {'Type' :'TERM_MATCH', 'Field':'instanceType', 'Value': instanceType},
             {'Type' :'TERM_MATCH', 'Field':'operation', 'Value': operation},
             {'Type' :'TERM_MATCH', 'Field':'location',  'Value': location}
         ],
         MaxResults=100
    )
    if len(response['PriceList']) == 0:
        raise Exception(f"pricing query returned 0 results. service {service}, instanceType {instanceType}, operation {operation}, location {location}")

    result = {}
    result['attributes'] = {}
    result['attributes']['service']= service
    result['attributes']['instanceType']= instanceType
    result['attributes']['operation']= operation
    result['attributes']['location']= location
    result['attributes']['region']= region
    result['attributes']['OfferingClass']= OfferingClass
    result['attributes']['PurchaseOption']= PurchaseOption
    result['attributes']['LeaseContractLength']= LeaseContractLength
    for price in response['PriceList']:
        jprice = json.loads(price)
        #print(json.dumps(jprice, indent=2))
        logging.debug(json.dumps(jprice, indent=2))
        for attribute in jprice['product']['attributes']:
            result['attributes'][attribute] = jprice['product']['attributes'][attribute]
        usagetype = jprice['product']['attributes']['usagetype']
        if 'Multi-AZUsage' in usagetype or 'Mirror' in usagetype:
            # Multi-AZ is always double
            continue
        for term in jprice['terms']:
            if term == 'Reserved':
                for key in jprice['terms'][term].keys():
                    if jprice['terms'][term][key]['termAttributes']['LeaseContractLength'] == LeaseContractLength and \
                       jprice['terms'][term][key]['termAttributes']['OfferingClass'] == OfferingClass and \
                       jprice['terms'][term][key]['termAttributes']['PurchaseOption'] == PurchaseOption :
                        result[term] = {}
                        for key2 in jprice['terms'][term][key]['priceDimensions'].keys():
                            unit  = jprice['terms'][term][key]['priceDimensions'][key2]['unit']
                            if unit == "Quantity":
                                result[term]['uf_price'] = \
                                    float(jprice['terms'][term][key]['priceDimensions'][key2]['pricePerUnit']['USD'])
                            elif unit == "Hrs":
                                result[term]['hr_price'] = \
                                    float(jprice['terms'][term][key]['priceDimensions'][key2]['pricePerUnit']['USD'])
                            descr = jprice['terms'][term][key]['priceDimensions'][key2]['description']
                            result[term]['description'] = descr
            elif term == 'OnDemand':
                for key in jprice['terms'][term].keys():
                    for key2 in jprice['terms'][term][key]['priceDimensions'].keys():
                        descr = jprice['terms'][term][key]['priceDimensions'][key2]['description']
                        if "per On Demand" in descr or "per RDS db" in descr:
                            unit  = jprice['terms'][term][key]['priceDimensions'][key2]['unit']
                            result[term] = {}
                            result[term]['unit'] = unit
                            result[term]['description'] = descr
                            if unit == "Hrs":
                                result[term]['hr_price'] = \
                                    float(jprice['terms'][term][key]['priceDimensions'][key2]['pricePerUnit']['USD'])
    if 'Reserved' not in result.keys():
        result['Reserved'] = {}
    elif 'hr_price' in result['Reserved'].keys():
        result['Reserved']['discount'] = round(
            1 - (result['Reserved']['hr_price'] / result['OnDemand']['hr_price'])
            ,2) *100
    if 'uf_price' in result['Reserved'].keys():
        # Calculate RI payback period
        result['Reserved']['payback_mos'] = round(result['Reserved']['uf_price'] / ((result['OnDemand']['hr_price']-result['Reserved']['hr_price'])*750),1)
    return result

@begin.subcommand()
def pricing(service=None, instanceType=None, operation=None, region=None, \
        LeaseContractLength='1yr', OfferingClass='standard', PurchaseOption='No Upfront', json_out=False):
    """ Prints AWS hourly usage pricing values for a resource type
    Called from CLI

    Args:
        service (str) : AWS service name. options 'AmazonEC2'|'AmazonRDS.
        instanceType (str) : Instance Type. e.x. 't2.micro' | 'db.t2.micro'
        operation (str) :  Operation. e.x. 'RunInstances' | 'RunINstances:0002' | 'CreateDBInstance:0014'
        region (str) : AWS region name. e.x 'us-east-1'
        LeaseContractLength (str) : RI contract length. default = '1yr'. options '1yr'|'3yr'
        OfferingClass (str) : RI offering class. default = 'standard'. options: 'standard'|'convertible'
        PurchaseOption (str) : RI purchase option. default = 'No Upfront'. options: 'All Upfront'|'Partial Upfront'|'No Upfront'
        json_out (bool): Print output as json
    Return
        bool: True
    """
    result = get_pricing(service=service, instanceType=instanceType, operation=operation, region=region, \
        LeaseContractLength=LeaseContractLength, OfferingClass=OfferingClass, PurchaseOption=PurchaseOption)
    if json_out:
        print(json.dumps(result, indent=2))
    else:
        #print(json.dumps(result, indent=2))
        print(f"Description: {result['OnDemand']['description']}")
        if 'operatingSystem' in result['attributes'].keys():
            print(f"OperatingSystem: {result['attributes']['operatingSystem']}")
        elif 'databaseEngine' in result['attributes'].keys():
            print(f"DB Engine: {result['attributes']['databaseEngine']}")
        print(f"CPU: ({result['attributes']['vcpu']})", end='')
        if 'clockSpeed' in result['attributes'].keys():
            print(f"{result['attributes']['clockSpeed']}", end="")
        print(f" {result['attributes']['physicalProcessor']}")
        print(f"Memory: {result['attributes']['memory']}")
        print(f"Network Performance: {result['attributes']['networkPerformance']}")
        print(f"RI LeaseContractLength: {LeaseContractLength}, OfferingClass: {OfferingClass}, PurchaseOption: {PurchaseOption}")
        if 'dedicatedEbsThroughput' in result['attributes'].keys():
            print(f"EBS Performance: {result['attributes']['dedicatedEbsThroughput']}")
        elif 'storage' in result['attributes'].keys():
            print(f"Storage: {result['attributes']['storage']}")
        print(f"OD Hourly Price: ${result['OnDemand']['hr_price']}")
        if 'hr_price' in result['Reserved'].keys():
            print(f"RI Hourly Price: ${result['Reserved']['hr_price']}")
        if 'uf_price' in result['Reserved'].keys():
            print(f"RI Upfront Price: ${result['Reserved']['uf_price']}")
        else:
            print(f"RI Upfront Price: $0.00")
        if 'discount' in result['Reserved'].keys():
            print(f"RI Hourly Discount: {round(result['Reserved']['discount'],2)}%")
        if 'payback_mos' in result['Reserved'].keys():
            print(f"RI Payback Period (mos): {result['Reserved']['payback_mos']}")

@begin.start
@begin.logging
def run():
    "Extracts pricing data from AWS"
