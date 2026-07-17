
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 250401826260.dkr.ecr.us-east-1.amazonaws.com

docker build -t x24266388-ecr-cpp:latest .

docker tag x24266388-ecr-cpp:latest 250401826260.dkr.ecr.us-east-1.amazonaws.com/x24266388-ecr-cpp:latest

docker push 250401826260.dkr.ecr.us-east-1.amazonaws.com/x24266388-ecr-cpp:latest