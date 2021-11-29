import socket
import threading
import pygame
import sys
import json
import csv
import os
from time import time 
from select import select
from network import send
import config as cfg

if len(sys.argv) < 3:
    raise RuntimeError(f"Not enough arguments, {len(sys.argv)}")

class Server:
    def __init__(self, host: str, port: int):
        # Get server's host IPv4 address
        self._host = host
        self._port = port

        self._to_client_connections = []
        self._from_client_connections = {}

        # Establish connection where clients can get game state update
        self._to_client_request = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._to_client_request.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Reuse socket
        self._to_client_request.bind((self._host, self._port))
        self._to_client_request.setblocking(False)

        # Establish connection where clients send control commands
        self._from_client_request = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._from_client_request.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Reuse socket
        self._from_client_request.bind((self._host, self._port + 1))
        self._from_client_request.setblocking(False)

        print(f"[NETWORK] ({self._host}, {self._port})")

        self._state = {}
        self._current_session_index = 0 
        self._counter = 0.0
        self._counter_target = 15.0

        self._game_paused = True
        self._exit_request = False
        self._thread_lock = threading.Lock()

        csv_data_path = "../data/"
        print(csv_data_path)
        if not os.path.exists(csv_data_path):
            os.makedirs(csv_data_path)

        self._csv_file = open(csv_data_path + str(int(time())) + ".csv", 'w', newline='')
        self._csv_writer = csv.writer(self._csv_file, delimiter=';')

    def run(self):
        """
        Set up threads for handling connections
        """
        to_client_request_thread = threading.Thread(target=self._dispatch_to_client_request, daemon=True)
        to_client_request_thread.start()

        from_client_request_thread = threading.Thread(target=self._dispatch_from_client_request, daemon=True)
        from_client_request_thread.start()

        from_client_commands_thread = threading.Thread(target=self._from_client_commands, daemon=True)
        from_client_commands_thread.start()

        to_client_update_state_thread = threading.Thread(target=self._to_client_update_state, daemon=True)
        to_client_update_state_thread.start()

        server_control_thread = threading.Thread(target=self._server_control, daemon=True)
        server_control_thread.start()

        # Wait for threads to finish
        server_control_thread.join()
        to_client_update_state_thread.join()
        to_client_request_thread.join()
        from_client_request_thread.join()
        from_client_commands_thread.join()

        # Close server connection
        self._to_client_request.close()
        self._from_client_request.close()

        self._csv_file.close()

    def _dispatch_to_client_request(self):
        """
        Dispatch client's connection for receiving game state updates from server
        """
        # Listen for client connection
        self._to_client_request.listen()

        while not self._exit_request:
            readable, _, _ = select([self._to_client_request], [], [self._to_client_request], 0.1)
            if readable:
                client_conn, client_addr = readable[0].accept()
                client_conn.setblocking(False)
                self._to_client_connections.append(client_conn)
                print("Sending replies to [" + client_addr[0] + ", " + str(client_addr[1]) + ']')

    def _dispatch_from_client_request(self):
        """
        Establish connection to receive clients' command
        """
        
        # Listen for client connection
        self._from_client_request.listen()

        while not self._exit_request:
            readable, _, _ = select([self._from_client_request], [], [self._from_client_request], 0.1)

            if readable:
                client_conn, client_addr = readable[0].accept()
                client_conn.setblocking(False)

                readable, _, _ = select([client_conn], [], [client_conn])
                if readable:
                    client_name = json.loads(readable[0].recv(cfg.HEADER).decode('utf-8'))
                else:
                    print("Connection closed")
                    continue
                
                self._thread_lock.acquire()
                self._from_client_connections[client_conn] = client_name
                self._state[client_name] = 0
                self._thread_lock.release()
                print("Receiving commands from [" + client_name + ", " + client_addr[0] + ", " + str(client_addr[1]) + ']')
                

    def _to_client_update_state(self):
        """
        Update game state then send game state updates to clients
        """
        clock = pygame.time.Clock() # Control the rate of sending data to clients
        while self._game_paused:
            start_ticks = pygame.time.get_ticks()
            
        while not self._exit_request:
            if not self._game_paused:
                seconds = (pygame.time.get_ticks() - start_ticks)/1000.0
                
                if self._counter > self._counter_target:
                    self._current_session_index += 1
                    #print("NEXT " + str(self._current_session_index))
                    if self._current_session_index >= len(cfg.SESSIONS):
                        self._exit_request = True
                        break
                    self._counter_target = cfg.SECONDS_PER_SESSION[self._current_session_index]
                    self._counter = 0.0
                    start_ticks = pygame.time.get_ticks()
                    
                elif seconds >= self._counter:
                    self._counter += 1.0
    
            data = {}
            data["message_type"] = "state"
            data["state"] = self._state
            data["session_index"] = self._current_session_index
            data["timer"] = int(self._counter_target - self._counter) + 1
            
            if not self._game_paused:
                self._csv_writer.writerow([time(), json.dumps(data)])

            _, writable, exceptional = select([], self._to_client_connections, self._to_client_connections, 0.0)
            for connection in writable:
                try:
                    send(connection, data)
                except:
                    print("Connection closed")
                    connection.close()
                    self._to_client_connections.remove(connection)
                    
            for connection in exceptional:
                connection.close()
                self._to_client_connections.remove(connection)
            if self._game_paused:
                clock.tick(2)
            else:
                clock.tick(10)

        while self._to_client_connections:
            _, writable, exceptional = select([], self._to_client_connections, self._to_client_connections)

            for connection in writable:
                data = {}
                data["message_type"] = "command"
                data["message"] = "CLOSE"

                try:
                    send(connection, data)
                except BrokenPipeError:
                    print("Connection closed")
                    #sys.exit()
                connection.close()
                self._to_client_connections.remove(connection)
            
            for connection in exceptional:
                connection.close()
                self._to_client_connections.remove(connection)
            
            clock.tick(60)

    def _from_client_commands(self):
        """
        Handle clients' commands
        """
        while not self._exit_request:
            readable, _, exceptional = select(self._from_client_connections.keys(), [], self._from_client_connections.keys(), 0.2)

            for connection in readable:
                client_name = self._from_client_connections[connection]

                message = connection.recv(cfg.HEADER)
                
                if not message:
                    continue
                try:
                    command = json.loads(message.decode('utf-8'))
                except json.decoder.JSONDecodeError as err:
                    print(err)
                    continue

                if command == "CLOSE":
                    connection.close()
                    self._thread_lock.acquire()
                    del self._from_client_connections[connection]
                    del self._state[client_name]
  
                    self._thread_lock.release()
                    ##sys.exit()
                '''
                elif command != "N/A":
                    
                    self._counter =  self._counter_target + 1.0
                '''
            for connection in exceptional:
                connection.close()
                self._thread_lock.acquire()
                del self._from_client_connections[connection]
                self._thread_lock.release()

        for connection in self._from_client_connections:
            connection.close()

    def _server_control(self):
        """
        Control the server 
        """
        while not self._exit_request:
            readable, _, _ = select([sys.stdin], [], [], 0.5)

            if not readable:
                continue

            command = readable[0].readline().strip()
            
            if command == "h" or command == "help":
                print("-----")
                print("exit: Close the server")
                print("pause: Pause the game")
                print("unpause: Unpause the game")
                print("h or help: List available commands")
                print("-----")
                
            elif command == "pause":
                self._game_paused = True

            elif command == "unpause":
                self._game_paused = False
                
            elif command == "exit":
                self._exit_request = True

            else:
                print("Unknown command")


if __name__ == "__main__":
    pygame.init()

    assert len(sys.argv) >= 2

    host = sys.argv[1]
    port = int(sys.argv[2])

    server = Server(host, port)
    server.run()
