python3.5 del_data.py
#rm -rf ~/.sovrin/Node*/
#rm -rf ~/.sovrin/Steward*/
#rm -rf ~/.sovrin/Sponsor*/
#rm -rf ~/.sovrin/data

rm -rf ~/.sovrin
rm -rf ~/.raet
rm -rf ~/.plenum

generate_sovrin_pool_transactions --nodes {{node_ips|length}} --clients 10 --nodeNum {{sovrin_node_number}} --ips {{node_ips | join(",")}}
