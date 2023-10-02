ACCOUNT_ID   := 576471727047
APP_NAME    := bandit-backend
VERSION     := $(shell poetry version --short)
REGION      := ap-northeast-2
CONTEXT     := arn:aws:eks:$(REGION):$(ACCOUNT_ID):cluster/eks-cluster-prod
ECR         := $(ACCOUNT_ID).dkr.ecr.$(REGION).amazonaws.com
DOCKER_REPO := "$(ECR)/$(APP_NAME):$(VERSION)"
GIT_BRANCH  := $(shell git rev-parse --abbrev-ref HEAD)

.PHONY: show-version \
		poetry-version \
		git-commit \
		git-push \
		docker-build \
		docker-tag \
		aws-login \
		aws-push \
		k8s-deploy \
		helm-install-prod \
		helm-uninstall-prod \
		snapshot \
		release-prod

show-version:
	@echo "=> New version: `poetry version --short`"

poetry-version: ## Increase the poetry version based on the SNAPSHOT_VERSION value (major, minor, or patch).
ifeq ($(SNAPSHOT_VERSION),minor)
	@echo "=> Incrementing minor version using poetry"
	@poetry version minor
else ifeq ($(SNAPSHOT_VERSION),major)
	@echo "=> Incrementing major version using poetry"
	@poetry version major
else
	@echo "=> Incrementing patch version using poetry"
	@poetry version patch
endif
	@make show-version

git-commit:
	@git add .
	@git commit -m "Update models to version `poetry version --short`"

git-push:
	@echo "GIT Pushing => $(GIT_BRANCH)"
	@git push origin $(GIT_BRANCH) --tags

compile: ## compile protobuf
	python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. protos/bandit.proto

docker-build:
	@echo "=> Building $(APP_NAME):$(VERSION)"
	docker buildx build \
	--build-arg GITHUB_TOKEN=$(GITHUB_TOKEN) \
	--platform=linux/amd64 \
	-t $(APP_NAME):$(VERSION) \
	-f Dockerfile .

docker-tag:
	@echo "=> Tagging $(APP_NAME):$(VERSION) as $(DOCKER_REPO)"
	docker tag $(APP_NAME):$(VERSION) $(DOCKER_REPO)

aws-login:
	@echo "=> Logging into AWS Account"
	aws ecr get-login-password --region $(REGION) | \
	docker login --username AWS --password-stdin $(ECR)

aws-push:
	@echo '=> Publishing $(APP_NAME):$(VERSION) to $(DOCKER_REPO)'
	docker push $(DOCKER_REPO)

helm-install-prod: ## Deploy bandit-backend-prod to K8s
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

helm-uninstall-prod:
	@echo "=> Uninstalling bandit-backend-prod"
	helm uninstall $(APP_NAME)-prod -n $(APP_NAME)-prod

snapshot: poetry-version git-commit git-push

release-prod: compile docker-build docker-tag aws-login aws-push helm-install-prod
