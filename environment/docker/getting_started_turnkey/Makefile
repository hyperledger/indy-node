SHELL := /bin/bash #bash syntax  
#
# ALICE Indy Sovrin Demo
#
# Setup a four node Indy Cluster, and four Indy clients called Indy, Faber, Acme, and Thrift 
#
# *** Make the indy-base docker image
#
#   make indy-base
#
# *** Run the first part of the Alice demo and then interactively run the rest of the demo
#
#    make run-demo
#
# *** Run the entire Alice demo
#
#    make run-alice
#
# *** Start a cluster and then start indy and agents (Only run the first time)
#    make cluster
#    make indy
#
# *** Start a cluster and then start indy prompt
#    make cluster
#    make indy-cli
#
# *** Start Faber only
#   make faber
#
# *** You can stop all docker containers
#   make stop
#
# *** Remove all docker containers
#   make clean
#

# Detect the local IP address
LOCAL:=$(shell ifconfig|grep 'inet '|grep -vm1 127.0.0.1|awk '{print $$2}' | sed -e 's/addr://g')

# Uncomment to manually set the local IP address if not set correctly above
# LOCAL=192.168.1.100

NO_COLOR="\x1b[0m"
OK_COLOR="\x1b[32;01m"
ERROR_COLOR="\x1b[31;01m"
WARN_COLOR="\x1b[33;01m"
BLUE_COLOR="\x1b[34;01m"


run-demo: clean info cluster faber acme thrift indy

run-alice: clean info cluster faber acme thrift indy-alice

indy-base:
	@echo -e  $(BLUE_COLOR)Indy-base Docker $(NO_COLOR)
	-docker rmi -f indy-base
	docker build -t indy-base -f ./indy-base-dockerfile .
	@echo -e  $(GREEN_COLOR)SUCCESS Indy-base Docker $(LOCAL) $(NO_COLOR)

local:
	@echo -e  $(BLUE_COLOR) Local IP is $(LOCAL) $(NO_COLOR)
	$(eval IPS=$(LOCAL),$(LOCAL),$(LOCAL),$(LOCAL))
	$(eval IPFABER=$(LOCAL))
	$(eval IPACME=$(LOCAL))
	$(eval IPTHRIFT=$(LOCAL))

info: local
	@echo -e  $(BLUE_COLOR) Settings.... $(NO_COLOR)
	@echo -e  $(BLUE_COLOR) IPS=$(IPS) $(NO_COLOR)
	@echo -e  $(BLUE_COLOR) IPFABER=$(IPFABER) $(NO_COLOR)
	@echo -e  $(BLUE_COLOR) IPACME=$(IPACME) $(NO_COLOR)
	@echo -e  $(BLUE_COLOR) IPTHRIFT=$(IPTHRIFT) $(NO_COLOR)

cluster:
	@echo -e  $(BLUE_COLOR) CLUSTER: Create 4 Nodes at IPS $(IPS) $(NO_COLOR)
	docker run --name Node1 -d -p 9701:9701 -p 9702:9702 indy-base /bin/bash -c "create_dirs.sh; init_indy_keys --name Node1; generate_indy_pool_transactions --nodes 4 --clients 5 --nodeNum 1 --ips $(IPS); start_indy_node Node1 9701 9702"
	docker run --name Node2 -d -p 9703:9703 -p 9704:9704 indy-base /bin/bash -c "create_dirs.sh; init_indy_keys --name Node2; generate_indy_pool_transactions --nodes 4 --clients 5 --nodeNum 2 --ips $(IPS); start_indy_node Node2 9703 9704"
	docker run --name Node3 -d -p 9705:9705 -p 9706:9706 indy-base /bin/bash -c "create_dirs.sh; init_indy_keys --name Node3; generate_indy_pool_transactions --nodes 4 --clients 5 --nodeNum 3 --ips $(IPS); start_indy_node Node3 9705 9706"
	docker run --name Node4 -d -p 9707:9707 -p 9708:9708 indy-base /bin/bash -c "create_dirs.sh; init_indy_keys --name Node4; generate_indy_pool_transactions --nodes 4 --clients 5 --nodeNum 4 --ips $(IPS); start_indy_node Node4 9707 9708"
	@echo -e  $(OK_COLOR) SUCCESS: Cluster 4 nodes success at IPS $(IPS) $(NO_COLOR)

indy-cli: info
	@echo -e  $(BLUE_COLOR) INDY DEBUG: Create Indy  $(IPS) $(NO_COLOR)
	docker run --rm --name IndyCli -it indy-base /bin/bash -c "create_dirs.sh; generate_indy_pool_transactions --nodes 4 --clients 5 --ips $(IPS); /bin/bash"

indy: info
	@echo -e  $(BLUE_COLOR) INDY: Create Indy and initialize with commandline jobs $(IPS) $(NO_COLOR)
	docker run --rm --name Indy -it indy-base /bin/bash -c "\
                        create_dirs.sh; generate_indy_pool_transactions --nodes 4 --clients 5 --ips $(IPS); \
			  ./indy-cli \
			  'connect sandbox' \
			  'new key with seed 000000000000000000000000Steward1' \
			  'send NYM dest=ULtgFQJe6bjiFbs7ke3NJD role=TRUST_ANCHOR verkey=~5kh3FB4H3NKq7tUDqeqHc1' \
			  'send NYM dest=CzkavE58zgX7rUMrzSinLr role=TRUST_ANCHOR verkey=~WjXEvZ9xj4Tz9sLtzf7HVP' \
			  'send NYM dest=H2aKRiDeq8aLZSydQMDbtf role=TRUST_ANCHOR verkey=~3sphzTb2itL2mwSeJ1Ji28' \
			  'new key with seed Faber000000000000000000000000000' \
			  'send ATTRIB dest=ULtgFQJe6bjiFbs7ke3NJD raw={\"endpoint\": {\"ha\": \"$(IPFABER):5555\", \"pubkey\": \"5hmMA64DDQz5NzGJNVtRzNwpkZxktNQds21q3Wxxa62z\"}}' \
			  'new key with seed Acme0000000000000000000000000000' \
			  'send ATTRIB dest=CzkavE58zgX7rUMrzSinLr raw={\"endpoint\": {\"ha\": \"$(IPACME):6666\", \"pubkey\": \"C5eqjU7NMVMGGfGfx2ubvX5H9X346bQt5qeziVAo3naQ\"}}' \
			  'new key with seed Thrift00000000000000000000000000' \
			  'send ATTRIB dest=H2aKRiDeq8aLZSydQMDbtf raw={\"endpoint\": {\"ha\": \"$(IPTHRIFT):7777\", \"pubkey\": \"AGBjYvyM3SFnoiDGAEzkSLHvqyzVkXeMZfKDvdpEsC2x\"}}' \
			  'save wallet'; \
			  /bin/bash \
		 	"
	@echo -e  $(OK_COLOR) SUCCESS: Indy $(NO_COLOR)

indy-alice: info
	@echo -e  $(BLUE_COLOR) INDY ALICE: Create Indy and initialize with commandline jobs $(IPS) $(NO_COLOR)
	docker run --rm --name IndyAlice -it indy-base /bin/bash -c "\
                        create_dirs.sh; generate_indy_pool_transactions --nodes 4 --clients 5 --ips $(IPS); \
			  ./indy-cli \
			  'connect sandbox' \
			  'new key with seed 000000000000000000000000Steward1' \
			  'send NYM dest=ULtgFQJe6bjiFbs7ke3NJD role=TRUST_ANCHOR verkey=~5kh3FB4H3NKq7tUDqeqHc1' \
			  'send NYM dest=CzkavE58zgX7rUMrzSinLr role=TRUST_ANCHOR verkey=~WjXEvZ9xj4Tz9sLtzf7HVP' \
			  'send NYM dest=H2aKRiDeq8aLZSydQMDbtf role=TRUST_ANCHOR verkey=~3sphzTb2itL2mwSeJ1Ji28' \
			  'new key with seed Faber000000000000000000000000000' \
			  'send ATTRIB dest=ULtgFQJe6bjiFbs7ke3NJD raw={\"endpoint\": {\"ha\": \"$(IPFABER):5555\", \"pubkey\": \"5hmMA64DDQz5NzGJNVtRzNwpkZxktNQds21q3Wxxa62z\"}}' \
			  'new key with seed Acme0000000000000000000000000000' \
			  'send ATTRIB dest=CzkavE58zgX7rUMrzSinLr raw={\"endpoint\": {\"ha\": \"$(IPACME):6666\", \"pubkey\": \"C5eqjU7NMVMGGfGfx2ubvX5H9X346bQt5qeziVAo3naQ\"}}' \
			  'new key with seed Thrift00000000000000000000000000' \
			  'send ATTRIB dest=H2aKRiDeq8aLZSydQMDbtf raw={\"endpoint\": {\"ha\": \"$(IPTHRIFT):7777\", \"pubkey\": \"AGBjYvyM3SFnoiDGAEzkSLHvqyzVkXeMZfKDvdpEsC2x\"}}' \
			  'save wallet' \
			  'prompt ALICE' \
			  'new wallet Alice' \
			  'load sample/faber-request.indy' \
			  'show connection Faber' \
			  'accept request from Faber' \
			  'show claim Transcript' \
			  'request claim Transcript' \
			  'show claim Transcript' \
			  'save wallet' \
			  'load sample/acme-job-application.indy' \
			  'accept request from Acme' \
			  'show proof request Job-Application' \
			  'set first_name to Alice' \
			  'set last_name to Garcia' \
			  'set phone_number to 123-456-7890' \
			  'show proof request Job-Application' \
			  'send proof Job-Application to Acme' \
			  'show connection Acme' \
			  'show claim Job-Certificate' \
			  'request claim Job-Certificate' \
			  'show claim Job-Certificate' \
			  'load sample/thrift-loan-application.indy' \
			  'accept request from Thrift' \
			  'show proof request Loan-Application-Basic' \
			  'send proof Loan-Application-Basic to Thrift' \
			  'show proof request Loan-Application-KYC' \
			  'send proof Loan-Application-KYC to Thrift' \
			  'save wallet' \
			  ; \
			  /bin/bash \
		 	"
	@echo -e  $(OK_COLOR) SUCCESS: Indy $(NO_COLOR)

faber:
	@echo -e  $(BLUE_COLOR) FABER: Create Faber $(IPS) $(NO_COLOR)
	docker run --rm --name Faber -d -p 5555:5555 indy-base /bin/bash -c "create_dirs.sh; generate_indy_pool_transactions --nodes 4 --clients 5 --ips $(IPS); sleep 40; python3 /usr/local/lib/python3.5/dist-packages/indy_client/test/agent/faber.py  --port 5555"
	@echo -e  $(OK_COLOR) Faber success assumes IPS $(IPS) $(NO_COLOR)

acme:
	@echo -e  $(BLUE_COLOR) ACME: Create Acme $(IPS) $(NO_COLOR)
	docker run --rm --name Acme -d -p 6666:6666 indy-base /bin/bash -c "create_dirs.sh; generate_indy_pool_transactions --nodes 4 --clients 5 --ips $(IPS); sleep 40; python3 /usr/local/lib/python3.5/dist-packages/indy_client/test/agent/acme.py  --port 6666"
	@echo -e  $(OK_COLOR) Acme success assumes IPS $(IPS) $(NO_COLOR)

thrift:
	@echo -e  $(BLUE_COLOR) THRIFT: Create Thrift $(IPS) $(NO_COLOR)
	docker run --rm --name Thrift -d -p 7777:7777 indy-base /bin/bash -c "create_dirs.sh; generate_indy_pool_transactions --nodes 4 --clients 5 --ips $(IPS); sleep 40; python3 /usr/local/lib/python3.5/dist-packages/indy_client/test/agent/thrift.py  --port 7777"
	@echo -e  $(OK_COLOR) Thrift success assumes IPS $(IPS) $(NO_COLOR)


stop:
	-docker stop Node1
	-docker stop Node2
	-docker stop Node3
	-docker stop Node4
	-docker stop Indy
	-docker stop IndyAlice
	-docker stop Faber
	-docker stop Acme
	-docker stop Thrift

start:
	-docker start Node1
	-docker start Node2
	-docker start Node3
	-docker start Node4
	-docker start Indy
	-docker start IndyAlice
	-docker start Faber
	-docker start Acme
	-docker start Thrift

clean:
	@echo -e  $(BLUE_COLOR) CLEAN out docker images and prune $(NO_COLOR)
	-docker rm -f Indy
	-docker rm -f IndyAlice
	-docker rm -f Faber
	-docker rm -f Acme
	-docker rm -f Thrift
	-docker rm -f Node1
	-docker rm -f Node2
	-docker rm -f Node3
	-docker rm -f Node4
