import psutil

cpus = psutil.cpu_count()
#print cpus

disk = psutil.disk_usage('/')
#print disk

conns = psutil.net_connections()
for con in conns:
	if "ESTABLISHED" in con:
		con = str(con)
		print con.split(" ")[5]
		

ifstats = psutil.net_if_stats()
#print ifstats
