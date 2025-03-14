REPO:=$(shell git remote -v | grep fetch | awk '{print $$2}' | sed 's/\.git$$//')
BRANCH:=$(shell git branch --show-current)
SUBDIR:=$(shell git rev-parse --show-prefix)

open-in-github:
	open -a "Google Chrome Dev" $(REPO)/tree/$(BRANCH)/$(SUBDIR)
