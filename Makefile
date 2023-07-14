APP_NAME=bandit-backend
VERSION=1.0.0.rc3
REGION=ap-northeast-2
ECR=576471727047.dkr.ecr.$(REGION).amazonaws.com
CLUSTER=eks-cluster-prod
CONTEXT=arn:aws:eks:$(REGION):576471727047:cluster/$(CLUSTER)
DOCKER_REPO="$(ECR)/$(APP_NAME):$(VERSION)"

compile: ## compile protobuf
	python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. protos/bandit.proto

unittest: ## Unittest execution
	@echo "=> Running unit tests"
	python -m pytest -v

build: ## Build the container
	@echo "=> Building $(APP_NAME):$(VERSION)"
	docker buildx build --platform=linux/amd64 -t $(APP_NAME):$(VERSION) -f Dockerfile .

tag: ## Tag the container
	@echo "=> Tagging $(APP_NAME):$(VERSION) as $(DOCKER_REPO)"
	docker tag $(APP_NAME):$(VERSION) $(DOCKER_REPO)

run: ## Run container on port 80
	@echo "=> Running $(APP_NAME):$(VERSION) on port 80"
	docker run -it -p 80:80 $(APP_NAME):$(VERSION)

login-aws: ## Login AWS Account
	@echo "=> Logining AWS Account"
	aws ecr get-login-password --region $(REGION) | \
	docker login --username AWS --password-stdin $(ECR)

push-aws: ## Publish the `{version}` tagged container to ECR
	@echo '=> Publishing $(APP_NAME):$(VERSION) to $(DOCKER_REPO)'
	docker push $(DOCKER_REPO)

install-dev: ## Deploy bandit-backend-dev to K8s
	cp .env.slave.k8s.dev helms/$(APP_NAME)/charts/slave/configs/.env.k8s.dev
	cp .env.master.k8s.dev helms/$(APP_NAME)/charts/master/configs/.env.k8s.dev
	@echo "=> Deploying bandit-backend-dev to K8s"
	helm upgrade \
	--create-namespace \
	--kube-context $(CONTEXT) \
	--namespace $(APP_NAME)-dev \
	--install -f helms/$(APP_NAME)/values.dev.yaml $(APP_NAME)-dev ./helms/$(APP_NAME)/ \
	--set master.image.tag=$(VERSION) \
	--set master.image.repository=$(ECR)/$(APP_NAME) \
	--set slave.image.tag=$(VERSION) \
	--set slave.image.repository=$(ECR)/$(APP_NAME)

install-prod: ## Deploy bandit-backend-prod to K8s
	cp .env.slave.k8s.prod helms/$(APP_NAME)/charts/slave/configs/.env.k8s.prod
	cp .env.master.k8s.prod helms/$(APP_NAME)/charts/master/configs/.env.k8s.prod
	@echo "=> Deploying bandit-backend-prod to K8s"
	helm upgrade \
	--create-namespace \
	--kube-context $(CONTEXT) \
	--namespace $(APP_NAME)-prod \
	--install -f helms/$(APP_NAME)/values.prod.yaml $(APP_NAME)-prod ./helms/$(APP_NAME)/ \
	--set master.image.tag=$(VERSION) \
	--set master.image.repository=$(ECR)/$(APP_NAME) \
	--set slave.image.tag=$(VERSION) \
	--set slave.image.repository=$(ECR)/$(APP_NAME)

uninstall-dev:
	@echo "=> Uninstalling bandit-backend-dev"
	helm uninstall $(APP_NAME)-dev -n $(APP_NAME)-dev

uninstall-prod:
	@echo "=> Uninstalling bandit-backend-prod"
	helm uninstall $(APP_NAME)-prod -n $(APP_NAME)-prod

release-dev: \
	compile build tag login-aws push-aws install-dev

release-prod: \
	compile build tag login-aws push-aws install-prod
