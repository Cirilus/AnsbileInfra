run:
	ansible-playbook init_server.yml

new:
	cd roles && ansible-galaxy role init $(name)