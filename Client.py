
import pygame
import sys
import threading
import socket
from select import select
from time import time 
import csv
import json
from network import send
import LoadImage as loadimg
import os

import config as cfg

if len(sys.argv) < 3:
    raise RuntimeError(f"Not enough arguments, {len(sys.argv)}")


class Client:
    def __init__(self):
        host = sys.argv[1]
        port = int(sys.argv[2])

        self._player_name = sys.argv[3]

        # Establish two-channel connection to server
        self._from_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._from_server.connect((host, port))
        self._from_server.setblocking(False)

        self._to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._to_server.connect((host, port + 1))
        self._to_server.setblocking(False)
        

        _, writable, _ = select([], [self._to_server], [self._to_server])
        try:
            send(writable[0], self._player_name)
        except BrokenPipeError:
            raise RuntimeError("Fail to establish connection with server")

        print("Connected to server, subject ID: " + self._player_name)

        self._running = True
        self.valence_score = "N/A"
        self.arousal_score = "N/A"
        self.submit_click = False

        self.image_path = " "
        csv_data_path = "../scoredata/"
        print(csv_data_path)
        if not os.path.exists(csv_data_path):
            os.makedirs(csv_data_path)

        self._csv_file = open(csv_data_path + str(int(time())) + ".csv", 'w', newline='')
        self._csv_writer = csv.writer(self._csv_file, delimiter=';')
        

    def button(self, screen, position, text):
        font = pygame.font.SysFont("Arial", 50)
        text_render = font.render(text, 1, (255, 0, 0))
        x, y, w , h = text_render.get_rect()
        x, y = position
        pygame.draw.line(screen, (150, 150, 150), (x, y), (x + w , y), 3)
        pygame.draw.line(screen, (150, 150, 150), (x, y - 2), (x, y + h), 3)
        pygame.draw.line(screen, (50, 50, 50), (x, y + h), (x + w , y + h), 3)
        pygame.draw.line(screen, (50, 50, 50), (x + w , y+h), [x + w , y], 3)
        pygame.draw.rect(screen, (100, 100, 100), (x, y, w , h))
        return screen.blit(text_render, (x, y))
    

    def run(self):
        """
        Run images on client's side
        """
        # Create a thread for sending client input to server
        control_thread = threading.Thread(target=self._send_input, daemon=True)
        control_thread.start()
        
        # Create a thread for controlling client from terminal
        client_control_thread = threading.Thread(target=self._client_control, daemon=True)
        client_control_thread.start()
        
        #loadimg = LoadImage()
        white = (255, 255, 255)
        green = (0, 255, 0)
        blue = (0, 0, 128)
        windowSurface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("MultiSubject Affective Task")
        
        
        while self._running:
            # Exit the game if user hits close
            
            # Get update from server about the state of the game
            readable, _, _ = select([self._from_server], [], [self._from_server])
            if readable:
                message = readable[0].recv(cfg.HEADER)

                if not message:
                    continue

                try:
                    data = json.loads(message.decode('utf-8'))
                except json.decoder.JSONDecodeError as err:
                    print(err)
                    continue

                # Exit game when server is closed
                if data["message_type"] == "command":
                    if data["message"] == "CLOSE":
                        self._running = False
                        print("Server closed")
                        break
            else:
                self._running = False
                print("Server closed")
                break
            #print(int(data["session_index"]))
            # Same till here at the least
            #print("RECEIVE")
            if data["session_index"] > 14:
                pygame.display.set_caption("MultiSubject Affective Task- Group")
            self.image_path = loadimg.imgs_path_list[int(data["session_index"])]
            img = pygame.image.load(loadimg.imgs_path_list[int(data["session_index"])])
            Arousal= pygame.image.load(loadimg.butt_path[0])
            Valence = pygame.image.load(loadimg.butt_path[1])
            Arousal_path = pygame.image.load(loadimg.butt_path[0])
            Valence_path = pygame.image.load(loadimg.butt_path[1])
            imgs_path = pygame.image.load(loadimg.imgs_path_list[data["session_index"]])
            rect_Arousal = Arousal_path.get_rect()
            rect_Valence = Valence_path.get_rect()

            rect = imgs_path.get_rect()
            arousal = pygame.transform.scale(Arousal_path, (850, 150))
            windowSurface.blit(imgs_path, (cfg.WIDTH//2 -  rect.centerx+450, cfg.HEIGHT//2 - rect.centery-160)) # Image in the center of the screen
            windowSurface.blit(Valence_path,(cfg.WIDTH//2 -  rect_Valence.centerx+450, cfg.HEIGHT//2 - rect_Valence .centery+450))
            windowSurface.blit(arousal,(cfg.WIDTH//2 -  rect_Arousal.centerx+450, cfg.HEIGHT//2 - rect_Arousal.centery+750))
   
            font = pygame.font.Font('freesansbold.ttf', 20)
            text_valence = font.render('Valence Score', True, green, blue)
            textRect_valence = text_valence.get_rect()
            textRect_valence.center = (cfg.WIDTH//2 -  rect_Valence.centerx+350, cfg.HEIGHT//2 - rect_Valence.centery+550)
            text_arousal = font.render('Arousal Score', True, green, blue)
            textRect_arousal = text_arousal.get_rect()
            textRect_arousal.center = (cfg.WIDTH//2 -  rect_Arousal.centerx+350, cfg.HEIGHT//2 - rect_Arousal.centery+825)
            if data["session_index"] > 14:
                text_title = font.render('MultiSubject Affective Task- Group Rating', True, green, blue)
            else:
                pygame.display.update()
                text_title = font.render('MultiSubject Affective Task- Individual', True, green, blue)
            textRect_title = text_title.get_rect()
            textRect_title.center = (cfg.WIDTH//2+500, cfg.HEIGHT//2+300)
            windowSurface.blit(text_title, textRect_title)
            windowSurface.blit(text_valence, textRect_valence)
            windowSurface.blit(text_arousal, textRect_arousal)
            
            
            if int(data["timer"]) < 16:
                if int(data["timer"]) < 10:
                    text_timer_text = font.render("Timer:", True, green, blue)
                    text_timer = font.render("0" + str(data["timer"]), True, green, blue)
                else:
                    text_timer_text = font.render("Timer:", True, green, blue)
                    text_timer = font.render(str(data["timer"]), True, green, blue)
                textRect_timer = text_timer.get_rect()
                textRect_timer_text = text_timer_text.get_rect()
                textRect_timer_text = (cfg.WIDTH//2 -  rect_Valence.centerx+220, cfg.HEIGHT//2 - rect_Arousal.centery+689)
                textRect_timer.center = (cfg.WIDTH//2 -  rect_Valence.centerx+300, cfg.HEIGHT//2 - rect_Arousal.centery+700) #position of the timer
                time = int(data["timer"])
                windowSurface.blit(text_timer, textRect_timer)
                windowSurface.blit(text_timer_text, textRect_timer_text)
                text_title.fill(pygame.Color("black"))
            
            v1 = self.button(windowSurface , (cfg.WIDTH//2 -  rect_Valence.centerx+500, cfg.HEIGHT//2 - rect_Valence.centery+650), "+2")
            v2 = self.button(windowSurface , (cfg.WIDTH//2 -  rect_Valence.centerx+675, cfg.HEIGHT//2 - rect_Valence.centery+650), "+1")
            v3 = self.button(windowSurface , (cfg.WIDTH//2 -  rect_Valence.centerx+850, cfg.HEIGHT//2 - rect_Valence.centery+650), "0")
            v4 = self.button(windowSurface , (cfg.WIDTH//2 -  rect_Valence.centerx+1025, cfg.HEIGHT//2 - rect_Valence.centery+650), "-1")
            v5 = self.button(windowSurface , (cfg.WIDTH//2 -  rect_Valence.centerx+1190, cfg.HEIGHT//2 - rect_Valence.centery+650), "-2")
            
            a1 = self.button(windowSurface , (cfg.WIDTH//2 -  rect_Arousal.centerx+500, cfg.HEIGHT//2 - rect_Arousal.centery+925), "+2")
            a2 = self.button(windowSurface , (cfg.WIDTH//2 -  rect_Arousal.centerx+675, cfg.HEIGHT//2 - rect_Arousal.centery+925), "+1")
            a3 = self.button(windowSurface , (cfg.WIDTH//2 -  rect_Arousal.centerx+850, cfg.HEIGHT//2 - rect_Arousal.centery+925), "0")
            a4 = self.button(windowSurface , (cfg.WIDTH//2 -  rect_Arousal.centerx+1025, cfg.HEIGHT//2 - rect_Arousal.centery+925), "-1")
            a5 = self.button(windowSurface , (cfg.WIDTH//2 -  rect_Arousal.centerx+1190, cfg.HEIGHT//2 - rect_Arousal.centery+925), "-2")
            
            submit = self.button(windowSurface, (cfg.WIDTH//2 -  rect_Valence.centerx+1400, cfg.HEIGHT//2 - rect_Valence.centery+670), "Submit")
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        self._running = False
                    # Notify server that client closes the connection
                        _, writable, _ = select([], [self._to_server], [self._to_server])
                        if writable:
                            send(writable[0], "CLOSE")
                        else:
                            raise RuntimeError("Lost connection with server")
                        
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if v1.collidepoint(pygame.mouse.get_pos()):
                        self.valence_score = +2
                    elif v2.collidepoint(pygame.mouse.get_pos()):
                        self.valence_score = +1
                    elif v3.collidepoint(pygame.mouse.get_pos()):
                        self.valence_score = 0
                    elif v4.collidepoint(pygame.mouse.get_pos()):
                        self.valence_score = -1
                    elif v5.collidepoint(pygame.mouse.get_pos()):
                        self.valence_score = +2
                    if a1.collidepoint(pygame.mouse.get_pos()):
                        self.arousal_score = +2
                    elif a2.collidepoint(pygame.mouse.get_pos()):
                        self.arousal_score = +1
                    elif a3.collidepoint(pygame.mouse.get_pos()):
                        self.arousal_score = 0
                    elif a4.collidepoint(pygame.mouse.get_pos()):
                        self.arousal_score = -1
                    elif a5.collidepoint(pygame.mouse.get_pos()):
                        self.arousal_score = -2
                    if submit.collidepoint(pygame.mouse.get_pos()):
                        self.submit_click = True
                        break
            if not self._running:
                break
            # Update client screen
            pygame.display.flip()
            
            
        # Close receiving connection
        self._from_server.close()

        # Close pygame window
        pygame.quit()

        # Wait for threads to finish
        control_thread.join()
        client_control_thread.join()
        self._csv_file.close()

    def _send_input(self):
        """
        Send user's input command to server
        """

        clock = pygame.time.Clock() # Control the rate of sending data to server
        while self._running:

            # Send control commands to server
            if self.submit_click == True:
                _, writable, _ = select([], [self._to_server], [self._to_server])
                score_data ={}
                score_data["client_name"] = self._player_name
                score_data["message_type"] = "SUBMIT"
                score_data["valence_score"] = self.valence_score
                score_data["arousal_score"] = self.arousal_score
                score_data["image_path"] = self.image_path
                self._csv_writer.writerow([time(), json.dumps(score_data)])
                for connection in writable:
                    try:
                        send(connection, score_data)
                        
                    except BrokenPipeError:
                        print("Server closed")
                        self._running = False
                self.submit_click = False
                self.valence_score = "N/A"
                self.arousal_score = "N/A"
            else:
                _, writable, _ = select([], [self._to_server], [self._to_server])
                if writable:
                    try:
                        send(writable[0], "N/A")
                    except BrokenPipeError:
                        print("Server closed")
                        self._running = False
                        

            # Limit loop rate to 60 loops per second
            clock.tick(60)
        
        # Close sending connection
        self._to_server.close()
        
    def _client_control(self):
        """
        Control client
        """
        while self._running:
            readable, _, _ = select([sys.stdin], [], [], 0.5)

            if not readable:
                continue

            command = readable[0].readline().strip()
            
            if command == "h" or command == "help":
                print("-----")
                print("exit: Close the game")
                print("h or help: List available commands")
                print("-----")
            elif command == "exit":
                self._running = False
                _, writable, _ = select([], [self._to_server], [self._to_server], 1.0)
                if writable:
                    try:
                        send(writable[0], "CLOSE")
                    except BrokenPipeError:
                        print("Server closed")
            else:
                print("Unknown command")

if __name__ == "__main__":
    pygame.init()

    client = Client()
    client.run()
