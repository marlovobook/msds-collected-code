REPO_NAME=${1:-erc-ml-streamlit}
PROFILE=${2:-ercml}
REGION=${3:-ap-southeast-1}
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text --profile $PROFILE)

# Build the Docker image
aws ecr describe-repositories --repository-names $REPO_NAME --profile $PROFILE> /dev/null 2>&1 || aws ecr create-repository --repository-name $REPO_NAME --profile $PROFILE

# Authenticate Docker to your default registry
aws ecr get-login-password --region $REGION  --profile $PROFILE | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Build the Docker image
docker buildx build  --platform linux/amd64 -t $REPO_NAME .

# Tag the Docker image
docker tag $REPO_NAME:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:latest

# Push the Docker image to ECR
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:latest