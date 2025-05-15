import boto3
import csv
import io
from datetime import datetime, timedelta

region_name = 'ap-south-1'  # Replace with your desired region
s3_client = boto3.client('s3', region_name=region_name)

# Initialize the EMR and CloudWatch clients
emr_client = boto3.client('emr')
cloudwatch_client = boto3.client('cloudwatch')
cloudtrail_client = boto3.client('cloudtrail')
s3_client = boto3.client('s3', region_name=region_name)


def get_job_details(cluster_id):
    response = emr_client.list_steps(ClusterId=cluster_id)
    job_details = []
    
    for step in response['Steps']:
        job_info = {
            'StepId': step['Id'],
            'Name': step['Name'],
            'Status': step['Status']['State'],
            'User': step.get('User', 'N/A'),
            'ApplicationType': step.get('HadoopJarStep', {}).get('Jar', 'N/A'),
            'StartDateTime': step.get('Status', {}).get('Timeline', {}).get('StartDateTime'),
            'EndDateTime': step.get('Status', {}).get('Timeline', {}).get('EndDateTime'),
            'Duration': step.get('Status', {}).get('Timeline', {}).get('EndDateTime') - step.get('Status', {}).get('Timeline', {}).get('StartDateTime')
        }
        job_details.append(job_info)

    return job_details

# Main function
def lambda_handler(event, context):
    cluster_id = 'j-PA6O9WC86NZ8'
    
    # Get job details
    job_details = get_job_details(cluster_id)
    
    # Print job details
    for job in job_details:
        print(f"Job ID: {job['StepId']}, Name: {job['Name']}, Status: {job['Status']}, User: {job['User']}, Application Type: {job['ApplicationType']}, Start: {job['StartDateTime']}, End: {job['EndDateTime']}, Duration: {job['Duration']}")

def get_application_details(cluster_id):
    response = emr_client.list_steps(ClusterId=cluster_id)
    steps = response['Steps']
    applications = []
    for step in steps:
        applications.append(step['Name'])
    return applications
    
def get_cluster_instances(cluster_id):
    response = emr_client.list_instances(ClusterId=cluster_id)
    return response['Instances']

    for instance in instances:
        instance_id = instance['Ec2InstanceId']
        print("Fetching steps for instance:", instance_id)
        response = emr_client.list_steps(ClusterId=cluster_id, InstanceId=instance_id)
        print("Response:", response)
        instance['Steps'] = response.get('Steps', [])
    return instances
    
    
def get_instance_metrics(instance_id):
    
    cpu_utilization_response = cloudwatch_client.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
        StartTime=datetime.utcnow() - timedelta(hours=1),
        EndTime=datetime.utcnow(),
        Period=600,  # 5-minute intervals
        Statistics=['Average']
    )
    if 'Datapoints' in cpu_utilization_response and cpu_utilization_response['Datapoints']:
        cpu_utilization = cpu_utilization_response['Datapoints'][-1]['Average']
    else:
        cpu_utilization = None

    memory_utilization_response = cloudwatch_client.get_metric_statistics(
        Namespace='CWAgent',
        MetricName='mem_used_percent',
        Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
        StartTime=datetime.utcnow() - timedelta(hours=1),
        EndTime=datetime.utcnow(),
        Period=300,  # 5-minute intervals
        Statistics=['Average']
    )
    if 'Datapoints' in memory_utilization_response and memory_utilization_response['Datapoints']:
        memory_utilization = memory_utilization_response['Datapoints'][-1]['Average']
    else:
        memory_utilization = None

        
    disk_utilization_response = cloudwatch_client.get_metric_statistics(
        Namespace='CWAgent',
        MetricName='disk_used_percent',
        Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
        StartTime=datetime.utcnow() - timedelta(hours=1),
        EndTime=datetime.utcnow(),
        Period=300,  
        Statistics=['Average']
    )
    if 'Datapoints' in disk_utilization_response and disk_utilization_response['Datapoints']:
        disk_utilization = disk_utilization_response['Datapoints'][-1]['Average']
    else:
        disk_utilization = None

    start_time = datetime.now() - timedelta(hours=2)
    end_time = datetime.now()
    
    num_cores = 4
    
    return cpu_utilization, memory_utilization, disk_utilization , start_time, end_time, num_cores

def get_cloudtrail_events(cluster_id):
    response = cloudtrail_client.lookup_events(
        LookupAttributes=[
            {'AttributeKey': 'ResourceName', 'AttributeValue': 'arn:aws:elasticmapreduce:region:account-id:cluster/{}'.format(cluster_id)}
        ],
        StartTime=datetime.utcnow() - timedelta(hours=1),
        EndTime=datetime.utcnow(),
    )
    events = response['Events']
    users = set()
    for event in events:
        if 'userIdentity' in event:
            user_identity = event['userIdentity']
            if 'userName' in user_identity:
                users.add(user_identity['userName'])
    return users

def create_bucket_if_not_exists(bucket_name, region_name):
    # Check if the bucket already exists
    response = s3_client.list_buckets()
    for bucket in response['Buckets']:
        if bucket['Name'] == bucket_name:
            return
    
    # If the bucket does not exist, create it
    try:
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={
                'LocationConstraint': region_name
            }
        )
    except s3_client.exceptions.ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'BucketAlreadyExists':
            # If the bucket already exists, return without doing anything
            return
        else:
            # For other errors, raise the exception
            raise
    

bucket_name = 'jobdetails1'
create_bucket_if_not_exists(bucket_name, region_name)

# Main function
def lambda_handler(event, context):
    cluster_id = 'j-PA6O9WC86NZ8'
    # Get users running applications on the EMR cluster
    users = get_user_running_applications(cluster_id)
    
    # Get application details
    applications = get_application_details(cluster_id)

    # Get users from CloudTrail events
    cloudtrail_users = get_cloudtrail_events(cluster_id)

    # Print user and application details
    print("Users running applications:", users)
    print("Applications:", applications)
    print("Users from CloudTrail events:", cloudtrail_users)
    
    # Get instances details
    instances = get_cluster_instances(cluster_id)
    data = []
    for instance in instances:
        cpu_utilization, memory_utilization, disk_utilization, start_time, end_time, num_cores = get_instance_metrics(instance['Ec2InstanceId'])
        data.append([
            instance['Ec2InstanceId'],
            instance['InstanceType'],
            instance['PrivateIpAddress'],
            cpu_utilization,
            memory_utilization,
            disk_utilization,
            start_time,
            end_time,
            num_cores
        ])
      # Write data to a CSV file in memory
    csv_buffer = io.StringIO()
    csv_writer = csv.writer(csv_buffer)
    csv_writer.writerow([
        "Instance ID",
        "Instance Type",
        "Private IP Address",
        "CPU Utilization",
        "Memory Utilization",
        "Disk Utilization",
        "Start Time",
        "End Time",
        "Number of Cores",
        "Application ID",
        "User   "
    ])
    csv_writer.writerows(data)
    for instance in instances:
        for step in instance['Steps']:
            application_id = step['Id']
            user = step.get('User', 'N/A')
            csv_writer.writerow([
                instance['Ec2InstanceId'],
                instance['InstanceType'],
                instance['PrivateIpAddress'],
                cpu_utilization,
                memory_utilization,
                disk_utilization,
                start_time,
                end_time,
                num_cores,
                application_id,
                user
            ])

    # Store CSV file in S3
    bucket_name = 'jobdetails1'
    file_name = 'emr_metrics.csv'
    s3_client.put_object(
        Bucket=bucket_name,
        Key=file_name,
        Body=csv_buffer.getvalue(),
        ContentType='text/csv'
    )
    for entry in data:
        print("Instance ID:", entry[0])
        print("Instance Type:", entry[1])
        print("Private IP Address:", entry[2])
        print("CPU Utilization:", entry[3])
        print("Memory Utilization:", entry[4])
        print("Disk Utilization:", entry[5])
        print("Start Time:", entry[6])
        print("End Time:", entry[7])
        print("Number of Cores:", entry[8])
        print("--------------------------")
    # No S3-related code here

    return {
        'statusCode': 200,
        'body': 'Metrics collected successfully'
    }