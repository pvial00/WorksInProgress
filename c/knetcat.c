#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#define PORT 6969

int main (int argc, char *argv[])
{
	char inbuf[16384];
	//while (fgets(inbuf, 128, stdin) != NULL ) {;
		//send(csock, inbuf, 16384, 0);
	//	printf("%s", inbuf);
	//}
	FILE *cmand;
        int sock, csock, recv_thread;
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
        if ((csock = accept(sock, (struct sockaddr *)&address,(socklen_t*)&addrlen))<0)
	{
                perror("Could not accept client");
                exit(EXIT_FAILURE);
	}
	printf("shit");
	//	char inbuf[16384];
	while (fgets(inbuf, 128, stdin) != NULL ) {;
		printf("check\n");
		send(csock, inbuf, 16384, 0);
		printf("%s", inbuf);
	}
	close(csock);
}
