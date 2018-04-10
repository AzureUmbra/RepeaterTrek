# RepeaterTrek

Currently in its infancy, RepeaterTrek will allow you to pull data from [RepeaterBook](https://www.repeaterbook.com/) and store it locally.  These local copies can be updated without having to pull a full repository again.  These repeaters can then be plotted on a map, with tooltips giving all of the information about them, including a link to it's page.  Finally, the primary use of RepeaterTrek is that it allows you to take a Google Maps trip and map out a your route with a list of all of the repeaters along your route.  This route can then be generated into a CHIRP file in order of your trip for easy radio programming!

## Getting Started

Currently the program exists as a single Python file with only definitions inside it.  Call the functions you want to run from the *main* function at the bottom.

### Prerequisites

- [Python 3.5](https://www.python.org/downloads/release/python-352/)
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)
```
pip install beautifulsoup4
```
- [Requests](http://docs.python-requests.org/en/master/)
```
pip install requests
```
- [gmplot](https://github.com/vgm64/gmplot)
```
pip install gmplot
```
- [geopy](https://github.com/geopy/geopy)
```
pip install geopy
```

### Installing

Once all the prerequisites are installed, just clone the repo and open *RepeaterTrek.py* in Idle.

```
git clone https://github.com/AzureUmbra/RepeaterTrek.git
```

## Basic Functions

### parseFromWeb

Pass the function the name of the state, and a URL to a RepeaterBook [Multi-State Search](https://www.repeaterbook.com/repeaters/multistate.php).  Additionally, pass it the same search while selecting *'Wide Area' Only* for wide area repeater functionality.
```
parseFromWeb('Texas','https://www.repeaterbook.com/repeaters/msResult.php?state_id%5B%5D=48&band=14&freq=&loc=&call=&features=%25&emcomm=%25&coverage=%25&status_id=1&order=%60freq%60%2C+%60state_abbrev%60+ASC',wideArea='https://www.repeaterbook.com/repeaters/msResult.php?state_id%5B%5D=48&band=14&freq=&loc=&call=&features=%25&emcomm=%25&coverage=wide&status_id=1&order=%60freq%60%2C+%60state_abbrev%60+ASC')
```
![RepeaterBook](https://github.com/AzureUmbra/RepeaterTrek/blob/master/img/RepeaterBook.JPG)

This will create a local repeater database for plotting your trips against.
```Requesting Repeater List
Repeaters Collected
Parsing Repeater Information
Requesting Repeater List
Repeaters Collected
Parsing Repeater Information
Repeaters Parsed and Sorted
Repeaters Parsed and Sorted
511 Repeaters Found
Beginning Location Collection
Getting Repeater Number 0 of 511
Getting Repeater Number 1 of 511
Getting Repeater Number 2 of 511
.
.
.
Getting Repeater Number 510 of 511
All Coordinates Received
Saved in File: TexasWA.rl
```

### updateFromWeb

Identical to above, this gets around the slow website issues and only checks for differences between your local list and the online list, so the slow initial download only has to happen once.
```
parseFromWeb('Texas','https://www.repeaterbook.com/repeaters/msResult.php?state_id%5B%5D=48&band=14&freq=&loc=&call=&features=%25&emcomm=%25&coverage=%25&status_id=1&order=%60freq%60%2C+%60state_abbrev%60+ASC',wideArea='https://www.repeaterbook.com/repeaters/msResult.php?state_id%5B%5D=48&band=14&freq=&loc=&call=&features=%25&emcomm=%25&coverage=wide&status_id=1&order=%60freq%60%2C+%60state_abbrev%60+ASC')
```
It will prompt you before any changes are made, and if any downloads need to happen.
```
511 Repeaters found of 503 in File
2 Repeaters Outdated
10 New Repeaters to Download
Enter "Y" to Delete Outdated and Download New: y
.
.
.
TexasWA.rl Updated to 511 Repeaters
```

### plotMap

Pass it a file name and it will generate a map.
```
plotMap('TexasWA')
Generating Map
Opening File TexasWA.rl
Map Saved as TesasWA.html
```
![Texas Image](https://github.com/AzureUmbra/RepeaterTrek/blob/master/img/Texas.JPG)

### blendMap

Pass it two or more maps and it will plot them together.
```
blendMap(['MississippiWA','AlabamaWA'],'MS and AL Blended')
Generating Map
Opening File MississippiWA.rl
Opening File AlabamaWA.rl
Map Saved as MS and AL Blended.html
```

![Blended Image](https://github.com/AzureUmbra/RepeaterTrek/blob/master/img/Blend.JPG)

### tripPlanner
Pass it a trip name, the repeater file names you want to consider, a max repeater distance, and a wide area repeater distance; and it will generate a map with start and end points, valid repeaters with data, and your route.
```
tripPlanner('Cross Texas',['TexasWA'],15,30)
```
Currently, you must go to [GPSVisualizer](http://www.gpsvisualizer.com/convert_input), copy the link from a Google Maps directions page into the *URL* box, select *comma* as the delimiter, and hit **convert**.  Copy this into a *.txt* file with the same name as your trip, and save it into the same directory as *RepeaterTrek.py*.

![GPS](https://github.com/AzureUmbra/RepeaterTrek/blob/master/img/GPS%20Visualizer.JPG)

```
Opening File TexasWA.rl
Getting Route Points
Checking Repeater 0 of 511
Checking Repeater 1 of 511
Checking Repeater 2 of 511
.
.
.
Checking Repeater 510 of 511
Found 94 Valid Repeaters
Trip Saved as Cross Texas.trip
Generating Map
Opening File Cross Texas.trip
Map Saved as Cross Texas.html
```
Now sit back and enjoy your map!

![Route Image](https://github.com/AzureUmbra/RepeaterTrek/blob/master/img/Route.JPG)

## Authors

* **[AzureUmbra](https://github.com/AzureUmbra)** - *Developer*

## License

This project is licensed under the GNU General Public License v3 - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* [Kostya Esmukov](https://github.com/KostyaEsmukov) for his geopy library, as I suck at haversin and great circle vector math.
* [Michael Woods](https://github.com/vgm64) for his gmplot library, without which the primary goal of this project would be dead.
