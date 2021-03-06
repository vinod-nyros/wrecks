import tags
import string
from myutil import *

catabs='''\
Alameda		8	31
Alpine		7	6
Amador		7	15
Butte		7	22
Calaveras		7	23
Colusa		7	10
Contra Costa		8	40
Del Norte		7	6
El Dorado		7	36
El Dorado	Placerville*	7.25	1
Fresno		7.625	51
Fresno	Clovis*	7.925	1
Glenn		7	8
Humboldt		7	52
Imperial		7.5	16
Imperial	Calexico*	8	1
Inyo		7.5	19
Kern		7	57
Kings		7	8
Lake		7	16
Lake		7.5	2
Lassen		7	18
Los Angeles		8	246
Los Angeles	Avalon*	8.5	1
Madera		7.5	11
Marin		7	32
Mariposa		7.5	16
Mendocino		7	29
Merced		7	21
Modoc		7	11
Mono		7	11
Monterey		7	36
Napa		7.5	14
Nevada		7.125	11
Nevada	Truckee*	7.625	1
Orange		7.5	58
Placer		7	29
Plumas		7	25
Riverside		7.5	72
Sacramento		7.5	29
San Benito		7	7
San Bernardino		7.5	101
San Diego		7.5	78
San Joaquin		7.5	21
San Luis Obispo		7	29
San Mateo		8	30
San Francisco		8.25	2
Santa Barbara		7.5	27
Santa Clara		8	33
Santa Cruz		7.75	21
Shasta		7	36
Sierra		7	8
Siskiyou		7	31
Solano		7.125	14
Sonoma		7.25	43
Stanislaus		7.125	21
Sutter		7	11
Tehama		7	14
Trinity		7	17
Tulare		7	47
Tuolumne		7	18
Ventura		7	23
Yolo		7	17
Yolo	Woodland*	7.5	1
Yuba		7	17'''

catax = ( \
('Alameda', '', '8', '31') , \
('Alpine', '', '7', '6') , \
('Amador', '', '7', '15') , \
('Butte', '', '7', '22') , \
('Calaveras', '', '7', '23') , \
('Colusa', '', '7', '10') , \
('Contra Costa', '', '8', '40') , \
('Del Norte', '', '7', '6') , \
('El Dorado', '', '7', '36') , \
('El Dorado', 'Placerville', '7.25', '1') , \
('Fresno', '', '7.625', '51') , \
('Fresno', 'Clovis', '7.925', '1') , \
('Glenn', '', '7', '8') , \
('Humboldt', '', '7', '52') , \
('Imperial', '', '7.5', '16') , \
('Imperial', 'Calexico', '8', '1') , \
('Inyo', '', '7.5', '19') , \
('Kern', '', '7', '57') , \
('Kings', '', '7', '8') , \
('Lake', '', '7', '16') , \
('Lake', 'Clearlake', '7.5', '2') , \
('Lassen', '', '7', '18') , \
('Los Angeles', '', '8', '246') , \
('Los Angeles', 'Avalon', '8.5', '1') , \
('Madera', '', '7.5', '11') , \
('Marin', '', '7', '32') , \
('Mariposa', '', '7.5', '16') , \
('Mendocino', '', '7', '29') , \
('Merced', '', '7', '21') , \
('Modoc', '', '7', '11') , \
('Mono', '', '7', '11') , \
('Monterey', '', '7', '36') , \
('Napa', '', '7.5', '14') , \
('Nevada', '', '7.125', '11') , \
('Nevada', 'Truckee', '7.625', '1') , \
('Orange', '', '7.5', '58') , \
('Placer', '', '7', '29') , \
('Plumas', '', '7', '25') , \
('Riverside', '', '7.5', '72') , \
('Sacramento', '', '7.5', '29') , \
('San Benito', '', '7', '7') , \
('San Bernardino', '', '7.5', '101') , \
('San Diego', '', '7.5', '78') , \
('San Joaquin', '', '7.5', '21') , \
('San Luis Obispo', '', '7', '29') , \
('San Mateo', '', '8', '30') , \
('San Francisco', '', '8.25', '2') , \
('Santa Barbara', '', '7.5', '27') , \
('Santa Clara', '', '8', '33') , \
('Santa Cruz', '', '7.75', '21') , \
('Shasta', '', '7', '36') , \
('Sierra', '', '7', '8') , \
('Siskiyou', '', '7', '31') , \
('Solano', '', '7.125', '14') , \
('Sonoma', '', '7.25', '43') , \
('Stanislaus', '', '7.125', '21') , \
('Sutter', '', '7', '11') , \
('Tehama', '', '7', '14') , \
('Trinity', '', '7', '17') , \
('Tulare', '', '7', '47') , \
('Tuolumne', '', '7', '18') , \
('Ventura', '', '7', '23') , \
('Yolo', '', '7', '17') , \
('Yolo', 'Woodland', '7.5', '1') , \
('Yuba', '', '7', '17') , \
)

calist = [ ('', 'Select CA County') ]

for (county, city, tax, count) in catax:
  tax = float (tax) + 0.25
  val = county + iff (city, ' (%s)' % city, '')
  val = val + ' %s%%' % (tax)
  if city: county = '%s.%s' % (county, city)
  nam = "(%s,'%s')" % (tax, county)
  calist.append ( (nam, val) )


if __name__ == "__main__":

  lines = string.split (catabs, '\n')
  
  for line in lines:
    toks = string.split (line, '\t')
    
      
    calist.append (tuple (toks))
  
  #print `calist`
  #for toks in calist:
  #  print `toks`, ', \\'

  #calist = []

  # lake county clearlake (2 entries) edited by hand, stars removed

  #for (county, city, tax, count) in catax:
  #  s = county + iff (city, ' (%s)' % city, '')
  #  s = s + ' %s%%' % float (tax)
  #  calist.append ( (tax, s) )

  print `calist`
  #print tags.select (tags.option (calist))

    

