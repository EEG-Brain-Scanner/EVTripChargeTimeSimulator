import pandas as pd
import plotly.graph_objects as go

df = pd.read_csv('/Users/evanskrukwa/Desktop/bdc/map/ev_stations.csv') #read csv
df = df[ df['EV DC Fast Count']>= 3 ] #remove stations with less than 3 fast chargers

#------------------------------US CHARGE POINT BRAND FIGURE------------------------------#

brandcountdf = df['EV Network'].value_counts().reset_index(name='count')
print(brandcountdf)

brandcolor = {'Tesla':'#C6353E', #red
              'Electrify America':'#19A103', #green
              'eVgo Network':'#163656', #dark blue
              'FCN':'#5E8EBF', #light blue
              'Non-Networked':'#000000', #black
              'EV Connect':'#7D00FF', #purple
              'Greenlots':'#FF6900', #oramge
              'EVCS':'#FF5CFA', #pink
              'FPLEV':'#707070', #grey
              'Blink Network': '#707070',
              'EVGATEWAY':'#707070'}
df['brandcolor'] = [brandcolor.get(x) for x in df['EV Network']] #update df with colors of brands

brandfig = go.Figure(data=go.Scattergeo( #make graph
        lon = df['Longitude'],
        lat = df['Latitude'],
        mode = 'markers',
        marker_color = df['brandcolor']))
brandfig.update_layout(
        geo_scope='usa')

brandfig.show()

#------------------------------US CHARGE POINT COMPATABILITY FIGURE------------------------------#

plugcountdf = df['EV Connector Types'].value_counts().reset_index(name='count')
print(plugcountdf)

def GetTypeCar(x): #figure out what typecar is from connectors available at station
    if 'J1772COMBO' not in x and 'CHADEMO' not in x:
        return('Tesla')
    elif 'J1772COMBO' in x and 'CHADEMO' in x:
        return('All')
    elif 'TESLA' not in x and 'CHADEMO' not in x:
        return('Most Brands')
    elif 'TESLA' not in x and 'J1772COMBO' not in x:
        return('Tesla and Exception Brands')

df['typecar'] = [GetTypeCar(x) for x in df['EV Connector Types']] #update df with typecar

typecar = {'Tesla':'#C6353E', #red
           'All':'#19A103', #green
           'Most Brands':'#707070', #grey
           'Tesla and Exception Brands':'#707070'}

typecartdf = df['typecar'].value_counts().reset_index(name='count')
print(typecartdf)

df['typecarcolor'] = [typecar.get(x) for x in df['typecar']] #update df with color of typecar
        
typecarfig = go.Figure(data=go.Scattergeo( #make graph
        lon = df['Longitude'],
        lat = df['Latitude'],
        mode = 'markers',
        marker_color = df['typecarcolor']))
typecarfig.update_layout(
        geo_scope='usa')

typecarfig.show()

#------------------------------US POPULATION FIGURE------------------------------#

censusdf = pd.read_csv('/Users/evanskrukwa/Desktop/bdc/map/2020citytown.csv') #read csv
censusdf = censusdf[ censusdf['Longitude']>= -130 ]#remove longitude less than -130
censusdf = censusdf[ censusdf['Population']>= 100 ]#remove pop less than 100

popfig = go.Figure(data=go.Scattergeo( #make graph
        lon = censusdf['Longitude'],
        lat = censusdf['Latitude'],
        mode = 'markers',
        marker = dict(
            size = censusdf['Population']/3000,
            line_color='rgb(40,40,40)',
            line_width=0.5,
            sizemode = 'area')))
popfig.update_layout(
        geo_scope='usa')

popfig.show()

#------------------------------OPENSTREETMAP API CODE------------------------------#

import requests
import json

root = 'http://router.project-osrm.org'
service = 'route'
version = 'v1'
profile = 'driving'

#c1... should be in format touple ex. c1 = (lat,long)

def GetDistance2(c1,c2):

    cordinates2 = ''.join((str(c1[1]),',',str(c1[0]),';',
                           str(c2[1]),','+str(c2[0])))
    
    r = requests.get('/'.join((root, service, version, profile, cordinates2)))
    l = json.loads(r.content)
    totald = l['routes'][0]['distance']
    return(totald/1609)

def GetDistance3(c1,c2,c3):

    cordinates3 = ''.join((str(c1[1]),',',str(c1[0]),';',
                           str(c2[1]),','+str(c2[0]),';',
                           str(c3[1]),','+str(c3[0])))
    
    r = requests.get('/'.join((root, service, version, profile, cordinates3)))
    l = json.loads(r.content)
    leg1d = l['routes'][0]['legs'][0]['distance']
    leg2d = l['routes'][0]['legs'][1]['distance']
    totald = l['routes'][0]['distance']
    return(leg1d/1609, leg2d/1609, totald/1609)

def GetDistance4(c1,c2,c3,c4):

    cordinates4 = ''.join((str(c1[1]),',',str(c1[0]),';',
                           str(c2[1]),','+str(c2[0]),';',
                           str(c3[1]),','+str(c3[0]),';',
                           str(c4[1]),','+str(c4[0])))
    
    r = requests.get('/'.join((root, service, version, profile, cordinates4)))
    l = json.loads(r.content)
    leg1d = l['routes'][0]['legs'][0]['distance']
    leg2d = l['routes'][0]['legs'][1]['distance']
    leg3d = l['routes'][0]['legs'][2]['distance']
    totald = l['routes'][0]['distance']
    return(leg1d/1609, leg2d/1609, leg3d/1609, totald/1609)

#------------------------------GET START AND END POINTS CODE------------------------------#

import random
#1 degree lattitude = 69 miles
#1 degree longitude (north end) = 44 miles
#1 degree longitude (south end) = 62 miles
#average = 53 miles
import math

def GetStartEnd():
    while True:
    
    
        n = random.randint(0,censusdf['Population'].sum()) #0 to all population known

        #range shifts numbers -1 to start at 0 so we +1 to start at 1 since 1st real row is df[0:1]

        for x in range(len(censusdf)):
            if n <= censusdf['Population'].iloc[0:x+1].sum(): #keep adding more rowns until number is encapsulated
                start = (censusdf.iloc[x]['Latitude'],censusdf.iloc[x]['Longitude'])
                break

        temp = censusdf[((censusdf['Latitude']<start[0]+300/69)&(censusdf['Latitude']>start[0]+300/69*0.6))|
                        ((censusdf['Latitude']>start[0]-300/69)&(censusdf['Latitude']<start[0]-300/69*0.6))|
                        ((censusdf['Longitude']<start[1]+300/53)&(censusdf['Longitude']>start[1]+300/53*0.6))|
                        ((censusdf['Longitude']>start[1]-300/53)&(censusdf['Longitude']<start[1]-300/53*0.6))]
        temp = temp[(temp['Latitude']<start[0]+300/69)&
                    (temp['Latitude']>start[0]-300/69)&
                    (temp['Longitude']<start[1]+300/53)&
                    (temp['Longitude']>start[1]-300/53)]

        global lastsquaredf
        lastsquaredf = temp #for the example graph function

        n = random.randint(0,temp['Population'].sum()) #0 to all population known

        #range shifts numbers -1 to start at 0 so we +1 to start at 1 since 1st real row is df[0:1]

        for x in range(len(temp)):
            if n <= temp['Population'].iloc[0:x+1].sum(): #keep adding more rowns until number is encapsulated
                end = (temp.iloc[x]['Latitude'],temp.iloc[x]['Longitude'])
                break

        d = float(GetDistance2(start,end) or 9*10^20)
        if d == 9*10^20:
            d = 'distance error'
        elif d < 330 and d > 270:
            return(start,end,d)

#------------------------------CLASIFY CHARGERS BASED OFF OF START AND END POINTS CODE------------------------------#

def CheckCharger(start, end, row):
    mp = ( (start[0]+end[0])/2 , (start[1]+end[1])/2 )
    d = math.sqrt( (start[0]-end[0])**2 + (start[1]-end[1])**2 )
    m = (start[1]-end[1]) / (start[0]-end[0])
    rad = math.atan(m)

    dl = d*1.1
    dh = d*0.5

    if (((row['Latitude']-mp[0])*(math.cos(rad)) + (row['Longitude']-mp[1])*(math.sin(rad)))**2) / ((dl/2)**2) + (((row['Latitude']-mp[0])*(math.sin(rad)) - (row['Longitude']-mp[1])*(math.cos(rad)))**2) / ((dh/2)**2) <= 1:
           return('maybe use')
    else:
        return('to far to consider')
         
#------------------------------GENERATE LIST OF CLASSIFIED CHARGERS BASED OFF OF START AND END POINTS CODE------------------------------#

def GetChargerList(start, end, df):
    
    df['inrange'] = df.apply(lambda row: CheckCharger(start, end, row), axis=1)
    df = df[ df['inrange']!= 'to far to consider' ]

    df = df[ df['typecar']!= 'Most Brands' ]

    return(df)

#------------------------------SIMPLE PYTHAG CODE------------------------------#    

def Pythag(cord1, cord2):
    return( math.sqrt( (cord1[0]-cord2[0])**2 + (cord1[1]-cord2[1])**2 ) )

#------------------------------DECIDE ON 1 OR 2 CHARGERS TO USE DURING TRIP CODE------------------------------#

def GetBestChargers(start, end, df):

    bestscore = 9**999
    finalc1 = 0
    finalc2 = 0
    
    for a in range(len(df)):
        for b in range(len(df)):
            charger1 = (df.iloc[a]['Latitude'],df.iloc[a]['Longitude'])
            charger2 = (df.iloc[b]['Latitude'],df.iloc[b]['Longitude'])

            q = Pythag(start, charger1)     #rough degree distance of leg 1
            w = Pythag(charger1, charger2)  #rough degree distance of leg 2
            e = Pythag(charger2, end)       #rough degree distance of leg 3

            d = q + w + e

            if a == b:
                d+=2 #2pt penalty for 1 supercharger meaning a 2 factor would still be able to win
                
                if q == 0:
                    highestmult = max(w,e) / min(w,e)
                elif w == 0:
                    highestmult = max(q,e) / min(q,e)
                else:
                    highestmult = max(q,w) / min(q,w)
            else:
                highestmult = max(q,w,e) / min(q,w,e)

            score = d + highestmult

            if score < bestscore and d < 10: #d<10 ignores trips that take likley would not be possible
                bestscore = score
                finalc1 = charger1
                finalc2 = charger2

    if bestscore == 9**999:
        return('trip not possible by cords')
    else:
        return(finalc1, finalc2)

#------------------------------CONVERT PERCENT OF BATTERY FROM 0% TO TIME IN MINUTES CODE------------------------------#

# y = (-100/63**2)(x-63**2)+100 where y is percent

def chargetime(percent):
    percent = percent*100
    return(63 - math.sqrt((percent-100)/(-100/63**2)))

#------------------------------SUMS TOTAL CHARGE TIME BASED ON LEG DISTANCES CODE------------------------------#

def GetTime3(d1, d2, d3):

    if d1 > 315 or d2 > 315 or d3 > 315:
        return('trip not possible by distance')
    
    leg1p, leg2p, leg3p = d1/315, d2/315, d3/315

    startingp = leg1p
    endingp = 0
    
    time = chargetime(leg1p) + chargetime(leg2p) + chargetime(leg3p) #time from 0% to end trip at 0%
    return(time)


def GetTime2(d1, d2):

    if d1 > 315 or d2 > 315:
        return('trip not possible by distance')
    
    leg1p, leg2p = d1/315, d2/315

    startingp = leg1p
    endingp = 0
    
    time = chargetime(leg1p) + chargetime(leg2p) #time from 0% to end trip at 0%
    return(time)

#------------------------------MAIN SIMULATION CODE------------------------------#

resultsdf = pd.DataFrame(columns = ['chargers','time','start','leg1','c1','leg2','c2','leg3','end'])

for x in range(len(df)):

    if x % 10 == 0: #progress updates
        print(x)

    try:

        for y in range(7):
            resultsdf = pd.read_csv('/Users/evanskrukwa/Downloads/results.csv')

            chargers = x + 1
            
            start, end, distance = GetStartEnd()
            
            listdf = GetChargerList(start, end, df.sample(frac=chargers/len(df)))

            finalchargers = GetBestChargers(start,end,listdf)
            if finalchargers == 'trip not possible by cords':
                time = 'trip not possible by cords'
                resultsdf = resultsdf.append([{'chargers':chargers,
                                                   'time':time,
                                                   'start':start,
                                                   'leg1':time,
                                                   'c1':time,
                                                   'leg2':time,
                                                   'c2':time,
                                                   'leg3':time,
                                                   'end':end}])

            else:
                c1,c2 = finalchargers

                if c1 == c2: #if trip uses 1 charge point
                    leg1, leg2, total = GetDistance3(start, c1, end)
                    time = GetTime2(leg1, leg2)
                    resultsdf = resultsdf.append([{'chargers':chargers,
                                                   'time':time,
                                                   'start':start,
                                                   'leg1':leg1,
                                                   'c1':c1,
                                                   'leg2':leg2,
                                                   'c2':'none',
                                                   'leg3':'none',
                                                   'end':end}])

                else: #if trip uses 2 charge points
                    leg1, leg2, leg3, total = GetDistance4(start, c1, c2, end)
                    time = GetTime3(leg1, leg2, leg3)
                    resultsdf = resultsdf.append([{'chargers':chargers,
                                                   'time':time,
                                                   'start':start,
                                                   'leg1':leg1,
                                                   'c1':c1,
                                                   'leg2':leg2,
                                                   'c2':c2,
                                                   'leg3':leg3,
                                                   'end':end}])

            resultsdf.to_csv('/Users/evanskrukwa/Downloads/results.csv', encoding='utf-8', index=False)
        
    except: #edge case errors do not stop the simulation
        resultsdf = resultsdf.append([{'chargers':'error',
                                        'time':'error',
                                       'start':'error',
                                       'leg1':'error',
                                       'c1':'error',
                                       'leg2':'error',
                                       'c2':'error',
                                       'leg3':'error',
                                       'end':'error'}])

        resultsdf.to_csv('/Users/evanskrukwa/Downloads/results.csv', encoding='utf-8', index=False)

#------------------------------EXAMPLE SIMULATION FIGURE------------------------------#

def ExampleGraph():
    
    global lastsquaredf
    start, end, d = GetStartEnd()

    temp = lastsquaredf

    temp['color'] = '#09213E'

    popstart = censusdf.loc[(censusdf['Latitude'] == start[0]) & (censusdf['Longitude'] == start[1])].iloc[0]['Population']

    popend = censusdf.loc[(censusdf['Latitude'] == end[0]) & (censusdf['Longitude'] == end[1])].iloc[0]['Population']

    temp = temp.append([{'Population':popstart,
                         'Latitude':start[0],
                         'Longitude':start[1],
                         'color':'#EC8533'}])

    temp = temp.append([{'Population':popend,
                         'Latitude':end[0],
                         'Longitude':end[1],
                         'color':'#EC8533'}])

    listdf = GetChargerList(start, end, df)

    for index, row in listdf.iterrows():
        temp = temp.append([{'Population':int(100000),
                             'Latitude':row['Latitude'],
                             'Longitude':row['Longitude'],
                             'color':'#B43141'}])

    fc1, fc2 = GetBestChargers(start,end,listdf)

    temp = temp.append([{'Population':int(300000),
                             'Latitude':fc1[0],
                             'Longitude':fc1[1],
                             'color':'#74FA4C'}])

    temp = temp.append([{'Population':int(300000),
                             'Latitude':fc2[0],
                             'Longitude':fc2[1],
                             'color':'#74FA4C'}])

    tempfig = go.Figure(data=go.Scattergeo(
        lon = temp['Longitude'],
        lat = temp['Latitude'],
        mode = 'markers',
        marker = dict(
            size = temp['Population']/3000,
            color = temp['color'],
            line_color='rgb(40,40,40)',
            line_width=0.5,
            sizemode = 'area')))
    tempfig.update_layout(
        geo_scope='usa')

    tempfig.show()
