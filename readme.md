# dualis api
This is an **unofficial API** for [dualis](https://www.dualis.dhbw.de) by DHBW (Cooperative State Univerity) built on 
top of Python Flask, Requests and Beautiful Soup. This is a student project and is not affiliated with DHBW.

## purpose
Checking for new marks in dualis can be very tedious. I thought, it would be great to automate it and spend your time on things
that count. That`s why I decided to create an API interface to query all your grades at once, 
which can then connect to all your apps and bots.

## usage
### sample request
Using the API is really simple as there is just one endpoint, that let's you query all grades from all semesters. Just 
pass in your credentials in the body of the GET request and you are good to go. Be aware, it might take a few seconds
until you receive a response, as the API has to make plenty of requests until all data is gathered (for my account it 
took around 20 sec.)
```
$ curl -i -H "Content-Type: application/json" -X GET -d '{"user":"karel.zeman@dhbw-karlsruhe.de","password":"journeyToTheCenterOftheEarth"}' http://localhost:5000/dualis/api/v1.0/grades/
```
### sample output
```
[
...
  {
    "name": "Fundamentals of IT (SU 2017)",
    "exams": [
      {
        "name": "Klausur (100%)",
        "date": "31.05.2017",
        "grade": "1,0",
        "externally accepted": ""
      },
      {
        "name": "Grundlegende Konzepte der IT (6)",
        "date": "",
        "grade": "100,0",
        "externally accepted": ""
      },
      {
        "name": "Kommunikations- und Betriebssysteme (9)",
        "date": "",
        "grade": "100,0",
        "externally accepted": ""
      }
    ]
  },
...
]
```
## installation
Installing is rather straight forward, but here is how you'd wanna do it.
### linux
```
$ wget https://github.com/KarelZe/dualis/archive/dualis.zip
$ unzip master.zip
$ mv dualis-master dualis
$ cd dualis
$ make
```

## todos
See the [issues tab](https://github.com/KarelZe/dualis/issues) for details.

## contact

Feel free to send me a mail at [github@markusbilz.com](mailto:github@markusbilz.com).
