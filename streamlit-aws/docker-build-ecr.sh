docker buildx build --platform linux/arm64 -t finalproject/msds0144 .
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 201213675728.dkr.ecr.us-east-1.amazonaws.com
docker tag finalproject/msds0144:latest 201213675728.dkr.ecr.us-east-1.amazonaws.com/finalproject/msds0144:latest
docker push 201213675728.dkr.ecr.us-east-1.amazonaws.com/finalproject/msds0144:latest