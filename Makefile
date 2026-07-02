.PHONY: help provision client-create client-config client-renew client-revoke client-rotate list-clients server-renew status

ANSIBLE_DIR := provisioning
INVENTORY ?= production
CLIENT ?=
INVENTORY_FILE := $(ANSIBLE_DIR)/inventories/$(INVENTORY)/hosts.yml
ANSIBLE_CONFIG := $(CURDIR)/$(ANSIBLE_DIR)/ansible.cfg
ANSIBLE_PLAYBOOK := ANSIBLE_CONFIG=$(ANSIBLE_CONFIG) ansible-playbook -i $(INVENTORY_FILE)
ANSIBLE_EXTRA_VARS := -e openvpn_local_clients_dir=$(CURDIR)/clients -e openvpn_inventory_name=$(INVENTORY)

help:
	@printf '%s\n' \
	'Usage:' \
	'  make provision INVENTORY=production' \
	'  make client-create INVENTORY=production CLIENT=alice' \
	'  make client-config INVENTORY=production CLIENT=alice' \
	'  make client-renew INVENTORY=production CLIENT=alice' \
	'  make client-revoke INVENTORY=production CLIENT=alice' \
	'  make client-rotate INVENTORY=production CLIENT=alice' \
	'  make list-clients INVENTORY=production' \
	'  make server-renew INVENTORY=production' \
	'  make status INVENTORY=production'

provision:
	$(ANSIBLE_PLAYBOOK) $(ANSIBLE_EXTRA_VARS) $(ANSIBLE_DIR)/provision.yml

client-create:
	@test -n "$(CLIENT)" || (echo "CLIENT is required"; exit 1)
	$(ANSIBLE_PLAYBOOK) $(ANSIBLE_EXTRA_VARS) -e openvpn_client_name=$(CLIENT) $(ANSIBLE_DIR)/client-create.yml

client-config:
	@test -n "$(CLIENT)" || (echo "CLIENT is required"; exit 1)
	$(ANSIBLE_PLAYBOOK) $(ANSIBLE_EXTRA_VARS) -e openvpn_client_name=$(CLIENT) $(ANSIBLE_DIR)/client-config.yml

client-renew:
	@test -n "$(CLIENT)" || (echo "CLIENT is required"; exit 1)
	$(ANSIBLE_PLAYBOOK) $(ANSIBLE_EXTRA_VARS) -e openvpn_client_name=$(CLIENT) $(ANSIBLE_DIR)/client-renew.yml

client-rotate: client-renew

client-revoke:
	@test -n "$(CLIENT)" || (echo "CLIENT is required"; exit 1)
	$(ANSIBLE_PLAYBOOK) $(ANSIBLE_EXTRA_VARS) -e openvpn_client_name=$(CLIENT) $(ANSIBLE_DIR)/client-revoke.yml

list-clients:
	$(ANSIBLE_PLAYBOOK) $(ANSIBLE_EXTRA_VARS) $(ANSIBLE_DIR)/list-clients.yml

server-renew:
	$(ANSIBLE_PLAYBOOK) $(ANSIBLE_EXTRA_VARS) $(ANSIBLE_DIR)/server-renew.yml

status:
	$(ANSIBLE_PLAYBOOK) $(ANSIBLE_EXTRA_VARS) $(ANSIBLE_DIR)/status.yml
