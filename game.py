def parse_game(game_file_path: str) -> dict:
     
     width:int=0
     height:int=0
     data:list[str]=[]
#

     try:
          with open(game_file_path, 'r') as file:
               data= [line.strip() for line in file]
          width=len(data[0].split('+')[1])

          height=len(data)-3
          max_moves:int=int(data[-1])
          cars=[line[1:-1] for line in data[1:-2]]

          carDict:dict[str, list[tuple[int, int], str, int]]={}

          for i in range(len(cars)):
               previous:str=''
               for j  in range(len(cars[i])):
                    car:str=cars[i][j].strip()
                    if(car=='.'):
                         previous='.'
                         continue
                    if car in carDict:
                         if(carDict[car][1]==''):
                              if previous==car:
                                   carDict[car][1]='h'

                              else:
                                   carDict[car][1]='v'
                         carDict[car][2]+=1
                    else:
                         carDict[car]= [(j,i),'',1]
                    previous=car

          carList:list[list[tuple[int, int], str, int]]=[value for key, value in sorted(carDict.items(), key=lambda item: item[0])]
          return {
               'width':width,
               'height':height,
               'cars':carList,
               'max_moves':max_moves
          }
     except FileNotFoundError:
          print(f"Error: The file '{game_file_path}' does not exist.")
          raise 
     except IOError as e:
          print(f"Error: An I/O error occurred while accessing '{game_file_path}': {e}")
          raise




def  get_game_str(game: dict, current_move_number: int) -> str:
     colors:list=['\u001b[41m','\u001b[42m','\u001b[43m','\u001b[44m','\u001b[45m','\u001b[46m']
     gameStr:list[list[str]]=[["." for _ in range(game['width'])] for _ in range(game['height'])]

     for k in range(len(game['cars'])):
          car=game['cars'][k]
          color=colors[(k-1)%len(colors)] if k!=0 else '\u001b[47m'
          (j,i)=car[0]
          for x in range(car[2]):
               gameStr[i][j]=color+chr(ord('A')+k)+'\u001b[0m'
               if car[1] == 'v':
                    i += 1
               else:
                    j += 1
     result='\n'.join([' '.join(e) for e in gameStr])
     result='Mouvements Effectués = '+str(game['max_moves']-current_move_number)+'\n'+result 
     result='Nombre de mouvements restants = '+str(current_move_number)+'\n'+result
     return result  













def move_car(game: dict, car_index: int, direction: str) ->bool:
     car:list=game['cars'][car_index]
     orientation:str=car[1]
     myCar:list=game['cars'][car_index]

     directions=['LEFT','RIGHT','UP','DOWN']

     if direction not in directions:
          return False
     elif (orientation=='h' and direction not in directions[:2]) or (orientation=='v' and direction not in directions[2:]):
          return False

     (i,j)=car[0]

     width:int=game['width']
     height:int=game['height']
     
     carlen:list=[] #position initiale et finale de chaque voiture
     borders:list=[]#nombre de cases libres dans les 2 directions de chaque voiture
     if orientation=='h':
          carlen=[i,i+car[2]-1]
          #borders=[left,right]
          borders=[i,width-i-car[2]]
     else:
          carlen=[j,j+car[2]-1]
          #borders=[up,down]
          borders=[j,height-j-car[2]]



     for car in game['cars']:
          if car!=myCar:

               if orientation=='h':
                    #on test si une voiture passe par le chemin de notre voiture
                    if (car[0][1] ==j ) or (car[1]=='v' and  car[0][1]<=j<=(car[0][1]+car[2]-1) ):
                         #si c'est le cas on calcule les distance pour modifier les bordures
                         if car[0][0]<i:
                              borders[0]=min(borders[0],i-car[0][0]-1)
                         else:
                              borders[1]=min(borders[1],car[0][0]-carlen[1]-1)
               else:
                    if(car[0][0]==i) or (car[1]=='h' and car[0][0]<=i<=(car[0][0]+car[2]-1)):
                         if(car[0][1]<j):
                              borders[0]=min(borders[0],j-car[0][1]-1)
                         else:
                              borders[1]=min(borders[1],car[0][1]-1-carlen[1])
     
     if direction=='RIGHT' and car_index==0 and borders[1]==0:#5ass ntester 3la l bordeeer dyal  la matrice machi cases libres
          game['cars'][car_index][0]=(i+1,j)
          return True
     
     indice_direction:int=directions.index(direction)
     border=indice_direction%2  #on match l'indice de la direction avec la border adequate

     if(borders[border]==0):
          return False
     
     else:
     
          if direction=='UP':
               game['cars'][car_index][0]=(i,j-1)
          elif direction=='DOWN':
               game['cars'][car_index][0]=(i,j+1)

          elif direction=='LEFT':
               game['cars'][car_index][0]=(i-1,j)

          elif direction=='RIGHT':
               game['cars'][car_index][0]=(i+1,j)


          return True
     





     


game_dict:dict=parse_game('game.txt')
print(get_game_str(game_dict,40))
# print(move_car(game_dict,0,'LEFT'))
# print(get_game_str(game_dict,40))
# print(move_car(game_dict,7,'DOWN'))
# print(get_game_str(game_dict,40))
# print(move_car(game_dict,6,'LEFT'))
# print(get_game_str(game_dict,40))