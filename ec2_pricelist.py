#!/usr/bin/env python3

import aws_pricing
import json
import sys

service = "AmazonEC2"
regions = ['us-east-1']
operations = {'Linux':'RunInstances', 'Windows':'RunInstances:0002', 'RHEL':'RunInstances:0010', 'Windows+SqlStnd':'RunInstances:0006'}
classes = ['t2', 't3', 'c4', 'c5', 'm4', 'm5', 'r5']
sizes = ['micro', 'small', 'medium', 'large', 'xlarge', '2xlarge']
ri_duration = '1yr'
ri_offerings = {'standard':'ri-std', 'convertible':'ri-cnvt'}
ri_options = {'No Upfront':'no-uf', 'Partial Upfront':'prt-uf', 'All Upfront':'all-uf'}

print("region,type-operation,ri_term,od_hr", end='')
for ri_offering in ri_offerings.keys():
    for ri_option in ri_options.keys():
        print(f",{ri_offerings[ri_offering]}_{ri_options[ri_option]}_hr", end='')
        print(f",{ri_offerings[ri_offering]}_{ri_options[ri_option]}_uf", end='' )
print('')
for region in regions:
    for klass in classes:
        for size in sizes:
            instance_type = f"{klass}.{size}"
            for operation in operations.keys():
                try:
                    pricing = aws_pricing.get_pricing(
                            service=service,
                            instanceType=instance_type,
                            operation=operations[operation],
                            region=region,
                            )
                    od_hr = pricing['OnDemand']['hr_price']
                except:
                    od_hr = None
                print(f"{region},{instance_type}-{operation},{ri_duration},{od_hr}", end='')
                for ri_offering in ri_offerings.keys():
                    for ri_option in ri_options.keys():
                        try:
                            pricing = aws_pricing.get_pricing(
                                    service=service,
                                    instanceType=instance_type,
                                    operation=operations[operation],
                                    region=region,
                                    LeaseContractLength=ri_duration,
                                    OfferingClass=ri_offering,
                                    PurchaseOption=ri_option
                                    )
                            od_hr = pricing['OnDemand']['hr_price']
                            ri_hr = pricing['Reserved']['hr_price']
                            if 'uf_price' in pricing['Reserved']: 
                                ri_uf = pricing['Reserved']['uf_price']
                            else:
                                ri_uf = 0.0
                        except:
                            ri_hr = None
                            ri_uf = None
                        print(f",{ri_hr},{ri_uf}", end='')
                print('')

