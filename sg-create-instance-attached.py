import boto3

ec2 = boto3.client('ec2')

# Replace the below values with your own
instance_id = 'i-0e6b4b63b9aedc15a'
security_groups_to_copy = ['sg-04e2c84c8e0cf2873']

# Get the instance name
instance = ec2.describe_instances(InstanceIds=[instance_id])
instance_vpc_id = instance['Reservations'][0]['Instances'][0]['VpcId']
instance_name = ''
for tag in instance['Reservations'][0]['Instances'][0]['Tags']:
    if tag['Key'] == 'Name':
        instance_name = tag['Value']
        break

# Copy the security groups and attach them to the instance
new_sg_ids = []
for sg_id in security_groups_to_copy:
    sg = ec2.describe_security_groups(GroupIds=[sg_id])
    sg_name = sg['SecurityGroups'][0]['GroupName']
    new_sg_name = instance_name + '-SG'
    ec2.create_tags(Resources=[new_sg['GroupId']], Tags=[{'Key': 'Name', 'Value': new_sg_name}])
    new_sg = ec2.create_security_group(GroupName=new_sg_name, Description=new_sg_name, VpcId=sg['SecurityGroups'][0]['VpcId'])
    ingress = sg['SecurityGroups'][0]['IpPermissions']
    egress = sg['SecurityGroups'][0]['IpPermissionsEgress']
    ec2.authorize_security_group_ingress(GroupId=new_sg['GroupId'], IpPermissions=ingress)
    ec2.authorize_security_group_egress(GroupId=new_sg['GroupId'], IpPermissions=egress)
    ec2.modify_instance_attribute(InstanceId=instance_id, Groups=[new_sg['GroupId']])
    new_sg_ids.append(new_sg['GroupId'])
print(f"Instance VpcId: {instance_vpc_id}")
print(f"New security group VpcId: {new_sg_vpc_id}")
print(new_sg)
print(f"Original SG ingress rules: {ingress}")
print(f"New SG ingress rules: {new_sg['IpPermissions']}")
print(f"Original SG egress rules: {egress}")
print(f"New SG egress rules: {new_sg['IpPermissionsEgress']}")

# Remove the previous security groups from the instance
instance_sg_ids = [sg['GroupId'] for sg in instance['Reservations'][0]['Instances'][0]['SecurityGroups']]
remove_sg_ids = list(set(instance_sg_ids) - set(new_sg_ids))
ec2.modify_instance_attribute(InstanceId=instance_id, Groups=new_sg_ids)
for sg_id in remove_sg_ids:
    ec2.modify_instance_attribute(InstanceId=instance_id, Groups=[sg_id])
