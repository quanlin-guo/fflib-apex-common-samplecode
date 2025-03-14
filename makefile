REPO_UPSTREAM:=$(shell git remote -v | grep fetch | grep upstream | awk '{print $$2}' | sed 's/\.git$$//')
REPO:=$(shell git remote -v | grep fetch | awk '{print $$2}' | grep origin | sed 's/\.git$$//')
BRANCH:=$(shell git branch --show-current)
SUBDIR:=$(shell git rev-parse --show-prefix)

open-in-github:
	open -a "Google Chrome Dev" $(REPO)/tree/$(BRANCH)/$(SUBDIR)

open-upstream-in-github:
	open $(REPO_UPSTREAM)/tree/$(BRANCH)/$(SUBDIR)
