import socket, select, threading

class SoundBoard:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    def server(self, host, port, listeners=1, recvlen=65536):
        self.recvlen = recvlen
        self.s.bind((host, int(port)))
        self.s.listen(listeners)
        self.sockets = []
        while True:
            c, addr = self.s.accept()
            self.sockets.append((c, addr))
            client_handle = threading.Thread(target=self.client_thread, args=(c,addr,)).start()

    def post(self, msg, addr):
        entry = addr[0] + str(addr[1]) + ":" + msg
        for sock in self.sockets:
            sock[0].send(entry)

    def removesocket(self, addr):
        for e, entry in enumerate(self.sockets):
            if entry[1] == addr:
                self.sockets.pop(e)

    def client_thread(self, socket, addr):
        self.post("User online\n", addr)
        while True:
            data = socket.recv(self.recvlen)
            if data == "exit\n":
                self.post("User logged out\n", addr)
                break
            else:
                self.post(data, addr)
        self.removesocket(addr)
        socket.close()
