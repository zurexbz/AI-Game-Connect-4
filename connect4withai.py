import numpy as np
import random
import pygame
import sys
import math
import os
os.getcwd()

#inisiasi variabel

# easy


diff_easy = {
    "name": "easy",
    "TOTAL_ROW": 6,
    "TOTAL_COLUMN": 7,
    "SZ_SQRT": 112,
}
diff_normal = {
    "name": "normal",
    "TOTAL_ROW": 7,
    "TOTAL_COLUMN": 8,
    "SZ_SQRT": 80,
}
diff_hard = {
    "name": "hard",
    "TOTAL_ROW": 9,
    "TOTAL_COLUMN": 10,
    "SZ_SQRT": 56,
}

def set_diff(diff):
    global TOTAL_ROW
    global TOTAL_COLUMN
    global SZ_SQR 
    global rad
    if diff == "normal": 
        TOTAL_ROW = diff_normal["TOTAL_ROW"]
        TOTAL_COLUMN = diff_normal["TOTAL_COLUMN"]
        SZ_SQR = diff_normal["SZ_SQRT"]
    elif diff == "hard":
        TOTAL_ROW = diff_hard["TOTAL_ROW"]
        TOTAL_COLUMN = diff_hard["TOTAL_COLUMN"]
        SZ_SQR = diff_hard["SZ_SQRT"]
    elif diff == "easy":
        TOTAL_ROW = diff_easy["TOTAL_ROW"]
        TOTAL_COLUMN = diff_easy["TOTAL_COLUMN"]
        SZ_SQR = diff_easy["SZ_SQRT"]
    rad = int(SZ_SQR/2 - 6)
    

PLAYER = 0
OPPONENT = 1
PLAYER_PIECE = 1
OPPONENT_PIECE = 2

#Inisiasi color
BLUE = (65,105,225)
RED = (255,0,0)
YELLOW = (255,255,0)
DARKBLUE = (14,0,51)
PURPLE = (184,30,173)
WHITE = (248,248,255)
WHITEPURPLE = (238, 209, 232)

def create_board(): #membuat board connect 4
	board = np.zeros((TOTAL_ROW,TOTAL_COLUMN))
	return board

def fill_board(board, row, column, piece): #menentukan posisi piece yang dijatuhkan
	board[row][column] = piece

def check_location(board, column): #cek memastikan lokasi yang bisa ditempati
	return board[TOTAL_ROW-1][column] == 0

def get_visited_board(board, column): #cek apakah baris sudah terisi
	for r in range(TOTAL_ROW):
		if board[r][column] == 0:
			return r

def print_board(board): #cetak board dengan keadaan terbalik dari bawah
	print(np.flip(board, 0))

def win_connection(board, piece): #cek koneksi untuk menang
	for c in range(TOTAL_COLUMN-3): #cek koneksi horizontal
		for r in range(TOTAL_ROW):
			if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
				return True

	for c in range(TOTAL_COLUMN): #cek koneksi vertikal
		for r in range(TOTAL_ROW-3):
			if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
				return True

	for c in range(TOTAL_COLUMN-3): #cek koneksi diagonal positif
		for r in range(TOTAL_ROW-3):
			if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
				return True

	for c in range(TOTAL_COLUMN-3): #cek koneksi diagonal negatif
		for r in range(3, TOTAL_ROW):
			if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
				return True

def player_score(window, piece):
	score = 0

	opp_piece = PLAYER_PIECE
	if piece == PLAYER_PIECE:
		opp_piece = OPPONENT_PIECE

	if window.count(piece) == 4:
		score += 100
	elif window.count(piece) == 3 and window.count(0) == 1:
		score += 5
	elif window.count(piece) == 2 and window.count(0) == 2:
		score += 2
	if window.count(opp_piece) == 3 and window.count(0) == 1:
		score -= 4

	return score

def score_position(board, piece):
	score = 0
	length = 4

	center_array = [int(i) for i in list(board[:, TOTAL_COLUMN//2])] ##score center
	center_count = center_array.count(piece)
	score += center_count * 3

	for r in range(TOTAL_ROW): #score horizontal
		row_array = [int(i) for i in list(board[r,:])]
		for c in range(TOTAL_COLUMN-3):
			window = row_array[c:c+length]
			score += player_score(window, piece)

	for c in range(TOTAL_COLUMN): #score vertikal
		column_array = [int(i) for i in list(board[:,c])]
		for r in range(TOTAL_ROW-3):
			window = column_array[r:r+length]
			score += player_score(window, piece)

	for r in range(TOTAL_ROW-3): #score diagonal positif
		for c in range(TOTAL_COLUMN-3):
			window = [board[r+i][c+i] for i in range(length)]
			score += player_score(window, piece)

	for r in range(TOTAL_ROW-3): #score diagonal negatif
		for c in range(TOTAL_COLUMN-3):
			window = [board[r+3-i][c+i] for i in range(length)]
			score += player_score(window, piece)

	return score

def terminal_node(board):
	return win_connection(board, PLAYER_PIECE) or win_connection(board, OPPONENT_PIECE) or len(get_valid_locations(board)) == 0

def abprunning(board, depth, alpha, beta, maximizingPlayer):
	valid_locations = get_valid_locations(board)
	terminal = terminal_node(board)
	if depth == 0 or terminal:
		if terminal:
			if win_connection(board, OPPONENT_PIECE):
				return (None, 100000000000000)
			elif win_connection(board, PLAYER_PIECE):
				return (None, -10000000000000)
			else:
				return (None, 0) #game over tidak ada ruang lagi
		else: #ketika depth 0
			return (None, score_position(board, OPPONENT_PIECE))
			
	if maximizingPlayer:
		value = -math.inf
		col = random.choice(valid_locations)
		for column in valid_locations:
			row = get_visited_board(board, column)
			b_copy = board.copy()
			fill_board(b_copy, row, column, OPPONENT_PIECE)
			new_score = abprunning(b_copy, depth-1, alpha, beta, False)[1]
			if new_score > value:
				value = new_score
				col = column
			alpha = max(alpha, value)
			if alpha >= beta:
				break
		return col, value

	else: # Minimizing player
		value = math.inf
		col = random.choice(valid_locations)
		for column in valid_locations:
			row = get_visited_board(board, column)
			b_copy = board.copy()
			fill_board(b_copy, row, column, PLAYER_PIECE)
			new_score = abprunning(b_copy, depth-1, alpha, beta, True)[1]
			if new_score < value:
				value = new_score
				col = column
			beta = min(beta, value)
			if alpha >= beta:
				break
		return col, value

def get_checkFull(board):
	check = []
	for column in range(TOTAL_COLUMN):
		if check_location(board, column):
			check.append(column)
	return check

def get_valid_locations(board):
	valid_locations = []
	for column in range(TOTAL_COLUMN):
		if check_location(board, column):
			valid_locations.append(column)
	return valid_locations

def draw_board(board):  
	for c in range(TOTAL_COLUMN):
		for r in range(TOTAL_ROW):
			pygame.draw.rect(screen, BLUE, (c*SZ_SQR, r*SZ_SQR+SZ_SQR, SZ_SQR, SZ_SQR))
			pygame.draw.circle(screen, WHITE, (int(c*SZ_SQR+SZ_SQR/2), int(r*SZ_SQR+SZ_SQR+SZ_SQR/2)), rad)
	print("DRAWBOARD", TOTAL_COLUMN, TOTAL_ROW, SZ_SQR)
	for c in range(TOTAL_COLUMN):
		for r in range(TOTAL_ROW):		
			if board[r][c] == PLAYER_PIECE:
				pygame.draw.circle(screen, YELLOW, (int(c*SZ_SQR+SZ_SQR/2), height-int(r*SZ_SQR+SZ_SQR/2)), rad)
			elif board[r][c] == OPPONENT_PIECE: 
				pygame.draw.circle(screen, RED, (int(c*SZ_SQR+SZ_SQR/2), height-int(r*SZ_SQR+SZ_SQR/2)), rad)
	pygame.display.update()
     


WIND_PART = 80
width = 7 * WIND_PART
height = (6 + 1) * WIND_PART
size = (width, height)


clock = pygame.time.Clock()
pygame.init()
pygame.display.set_caption('Connect 4 Game')
screen = pygame.display.set_mode(size)

fontsizeA =pygame.font.Font("waghu.otf", 50)
fontsizeB = pygame.font.Font("waghu.otf",30)
fontsizeC = pygame.font.Font("waghu.otf",20)
fontsizeD = pygame.font.Font("waghu.otf", 25)
fontGothic = pygame.font.Font("GOTHIC.TTF",15)
background = pygame.image.load('homepage.jpg')
background = pygame.transform.scale(background, (size))
pygame.mixer.music.load("music.wav")
pygame.mixer.music.play(-1) 


def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.center = (width/2 + x , height/2 + y )
    surface.blit(textobj, textrect)

def main_menu(click):
    while True:
        screen.fill(DARKBLUE)
        screen.blit(background, (0,0))
        draw_text('CONNECT 4 GAME', fontsizeA, PURPLE, screen, 0, -95)
        draw_text('SELECT MODE', fontsizeB, PURPLE, screen, 0, -15)
        
        mx, my = pygame.mouse.get_pos()
        vsai = pygame.Rect(192, 287, 176, 40)
        vsfriend = pygame.Rect(210, 335, 137, 40)
        abot = pygame.Rect(8, 520, 32, 32)
        exit = pygame.Rect(502, 520, 50, 32)

        pygame.draw.rect(screen, WHITEPURPLE, vsai, 3, 12)
        pygame.draw.rect(screen, WHITEPURPLE, vsfriend, 3, 12)
        pygame.draw.rect(screen, WHITEPURPLE, abot, 0, 12)
        pygame.draw.rect(screen, WHITEPURPLE, exit, 0, 12)

        draw_text('VS COMPUTER', fontsizeD, WHITEPURPLE, screen, 0, 27)
        draw_text('VS FRIEND', fontsizeD, WHITEPURPLE, screen, 0, 76)
        draw_text('?', fontsizeB, PURPLE, screen, -258, 255)
        draw_text('EXIT', fontsizeC, PURPLE, screen, 247, 256)
        
        if abot.collidepoint((mx, my)):
            if click:
                about(click)
        if vsai.collidepoint((mx, my)):
            if click:
                difficulty(1)
        if vsfriend.collidepoint((mx, my)):
            if click:
                difficulty(2)
        if exit.collidepoint((mx, my)):
            if click:
                pygame.quit()
                sys.exit()
        
        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
        
        pygame.display.update()
        clock.tick(60)

# add difficulty
def difficulty(vs):
    click = False
    while True:
        screen.fill(DARKBLUE)
        screen.blit(background, (0,0))
        draw_text('SELECT DIFFICULTY LEVEL!', fontsizeB, PURPLE, screen, 0, -55)
        
        mx, my = pygame.mouse.get_pos()
        easy = pygame.Rect(192, 287, 176, 40)
        normal = pygame.Rect(192, 335, 176, 40)
        hard = pygame.Rect(192, 383, 176, 40)

        pygame.draw.rect(screen, WHITEPURPLE, easy, 3, 12)
        pygame.draw.rect(screen, WHITEPURPLE, normal, 3, 12)
        pygame.draw.rect(screen, WHITEPURPLE, hard, 3, 12)

        draw_text('EASY', fontsizeD, WHITEPURPLE, screen, 0, 27)
        draw_text('NORMAL', fontsizeD, WHITEPURPLE, screen, 0, 76)
        draw_text('HARD', fontsizeD, WHITEPURPLE, screen, 0, 125)
        
        if vs == 1:
            if easy.collidepoint((mx, my)):
                if click:
                    game_with_AI(diff_easy["name"])
            if normal.collidepoint((mx, my)):
                if click:
                    game_with_AI(diff_normal["name"])
            if hard.collidepoint((mx, my)):
                if click:
                    game_with_AI(diff_hard["name"])
        else:
            if easy.collidepoint((mx, my)):
                if click:
                    game_two_players(diff_easy["name"])
            if normal.collidepoint((mx, my)):
                if click:
                    game_two_players(diff_normal["name"])
            if hard.collidepoint((mx, my)):
                if click:
                    game_two_players(diff_hard["name"])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
        pygame.display.update()
        clock.tick(60)

def about(click):
    while True:
        screen.fill(DARKBLUE)
        screen.blit(background, (0, 0))
        draw_text('How to Play', fontsizeA, PURPLE , screen, 0, -100)
        draw_text('1. Setiap pemain memainkan giliran bermain secara bergantian', fontGothic, WHITE , screen, -0, -45)
        draw_text('2. Pemain dapat mengisi lingkaran kosong untuk diisi', fontGothic, WHITE , screen, -42, -25)
        draw_text('3. Lakukan secara bergantian hingga mencapai koneksi 4 beruntun', fontGothic, WHITE , screen, 15, -5)
        draw_text('4. Koneksi menang adalah horizontal, vertical, dan diagonal', fontGothic, WHITE , screen, -14, 15)
        draw_text('Contoh koneksi seperti gambar berikut →', fontGothic, WHITE , screen, -82, 55)
        
        mx, my = pygame.mouse.get_pos()
        tomenu = pygame.Rect(492, 8, 60, 32)
        pygame.draw.rect(screen, WHITEPURPLE, tomenu, 0, 3)
        draw_text('BACK', fontsizeC, PURPLE, screen, 242, -256)

        image = pygame.image.load("connection.png")
        image = pygame.transform.scale(image, (110, 100))
        screen.blit(image, (355,330))
        
        if tomenu.collidepoint((mx, my)):
            if click:
                main_menu(click)
        
        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

        pygame.display.update()
        clock.tick(60) 

def game_with_AI(diff) :
    set_diff(diff)
    print(TOTAL_COLUMN, TOTAL_ROW, SZ_SQR)
    click = False
    running = True
    turn = 0    
    while running :
        screen.fill(DARKBLUE)
        draw_text('GAME START!', fontsizeA, PURPLE, screen, 0, -240)
        board = create_board()
        print_board(board)
        draw_board(board)
        game_over = False

        while not game_over :
            for event in pygame.event.get():
                #untuk keluar dari tampilan
                if event.type == pygame.QUIT:
                    sys.exit()

                #yang ditampilkan pada gerakan mouse
                if event.type == pygame.MOUSEMOTION:
                    pygame.draw.rect(screen, DARKBLUE,(0,0, width, SZ_SQR))
                    posx = event.pos[0]
                    if turn == 0:
                        pygame.draw.circle(screen, YELLOW, (posx, int(SZ_SQR/2)), rad )
                pygame.display.update()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pygame.draw.rect(screen, DARKBLUE,(0,0, width, SZ_SQR))
                    if turn == 0:
                        posx = event.pos[0]
                        kolom = int(math.floor(posx/SZ_SQR))          
                        if check_location(board, kolom):
                            baris = get_visited_board(board,kolom)
                            fill_board(board, baris,kolom, PLAYER_PIECE)
                            if win_connection(board, PLAYER_PIECE):
                                label = fontsizeA.render("         YOU WIN!!!", 1, YELLOW)
                                screen.blit(label,(40,15))
                                game_over = True
                            turn += 1
                            turn = turn%2
                            print_board(board)
                            draw_board(board)
                        else:
                            print("Column full")
                            pygame.quit()
            
            if turn == 1 and not game_over:  
                kolom, alpha_beta_score = abprunning(board, 2, -math.inf, math.inf, True)
                if check_location(board, kolom):
                    baris = get_visited_board(board,kolom)
                    fill_board(board, baris,kolom, OPPONENT_PIECE)
                    if (fill_board):
                        pop = pygame.mixer.Sound("pop.wav")
                        pop.play()
                    if win_connection(board, OPPONENT_PIECE):
                        label = fontsizeA.render("    COMPUTER WIN !!!", 1, RED)
                        screen.blit(label,(60,15))
                        game_over = True

                    print_board(board)
                    draw_board(board)
                    turn += 1
                    turn = turn%2
                    
            if game_over:
                pygame.time.wait(3000)
                main_menu(click)
    
    pygame.display.update()
    clock.tick(60)

def game_two_players(diff):
    set_diff(diff)
    click = False
    running = True
    turn = 0    
    while running :
        screen.fill(DARKBLUE)
        draw_text('GAME START!', fontsizeA, PURPLE, screen, 0, -240)
        board = create_board()
        print_board(board)
        draw_board(board)
        game_over = False 
        
        while not game_over :
            for event in pygame.event.get():
                #untuk keluar dari tampilan
                if event.type == pygame.QUIT:
                    sys.exit()

                #yang ditampilkan pada gerakan mouse
                if event.type == pygame.MOUSEMOTION:
                    pygame.draw.rect(screen, DARKBLUE,(0,0, width, SZ_SQR))
                    posx = event.pos[0]
                    if turn == 0:
                        pygame.draw.circle(screen, YELLOW, (posx, int(SZ_SQR/2)), rad)
                    else:
                        pygame.draw.circle(screen, RED, (posx, int(SZ_SQR/2)), rad)
                pygame.display.update()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pygame.draw.rect(screen, DARKBLUE,(0,0, width, SZ_SQR))
                
                    #Meminta input dari player 1
                    if turn == 0:
                        posx = event.pos[0]
                        kolom = int(math.floor(posx/SZ_SQR))     

                        if check_location(board, kolom):
                            baris = get_visited_board(board,kolom)
                            fill_board(board, baris,kolom, PLAYER_PIECE)
                            if (fill_board):
                                pop = pygame.mixer.Sound("pop.wav")
                                pop.play()
                            if win_connection(board, PLAYER_PIECE):
                                label = fontsizeA.render("        PLAYER 1 WIN!!!", 1, YELLOW)
                                screen.blit(label,(40,15))
                                game_over = True

                    #Meminta input dari player2
                    else:  
                        posx = event.pos[0]
                        kolom = int(math.floor(posx/SZ_SQR))

                        if check_location(board, kolom):
                            baris = get_visited_board(board,kolom)
                            fill_board(board, baris,kolom, OPPONENT_PIECE)
                            if (fill_board):
                                pop = pygame.mixer.Sound("pop.wav")
                                pop.play()

                            if win_connection(board, OPPONENT_PIECE):
                                label = fontsizeA.render("        PLAYER 2 WIN !!!", 1, RED)
                                screen.blit(label,(40,15))
                                game_over = True

                    print_board(board)
                    draw_board(board)

                    #Untuk update giliran permainan
                    turn += 1
                    turn = turn%2
                    
                    if game_over:
                        pygame.time.wait(3000)
                        main_menu(click)
    
    pygame.display.update()
    clock.tick(60)

click = False
main_menu(click)