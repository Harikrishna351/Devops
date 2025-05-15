#!/bin/bash

# Fetch instance ID and region
INSTANCE_ID=$(wget -qO- http://instance-data/latest/meta-data/instance-id)
REGION=$(wget -qO- http://instance-data/latest/meta-data/placement/availability-zone | sed -e 's:\([0-9][0-9]*\)[a-z]*$:\1:')

# Replace TAG_NAME with the actual tag name you want to use
TAG_NAME="YourTagName"
TAG_VALUE=$(aws ec2 describe-tags --filters "Name=resource-id,Values=$INSTANCE_ID" "Name=key,Values=$TAG_NAME" --region $REGION --output=text | cut -f5)
echo $TAG_VALUE

echo "Installing additional Perl modules"
sudo dnf install -y perl-Switch perl-DateTime perl-Sys-Syslog perl-LWP-Protocol-https perl-Digest-SHA

echo "Installing CloudWatch Logs agent"
sudo dnf install -y awslogs
echo "Downloading and installing the CloudWatch Agent"
curl -O https://amazoncloudwatch-agent.s3.amazonaws.com/amazon_linux/arm64/latest/amazon-cloudwatch-agent.rpm
sudo rpm -Uvh amazon-cloudwatch-agent.rpm


sudo chmod +x /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard


echo "Setting up cron job for monitoring"
# Cron job to run the monitoring script every 2 minutes
crontab -l 2>/dev/null; echo "*/2 * * * * /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c file:$CONFIG_FILE -s --mem-used-incl-cache-buff --mem-util --disk-space-util --disk-path=/ --disk-path=/mnt --disk-path=/mnt1 --disk-path=/emr --disk-path=/mnt2 --disk-path=/mnt3" | crontab -

echo "Configuration complete."
