<h1 align=center>abrix</h1>

<div align=center>

![GitHub last commit](https://img.shields.io/github/last-commit/ProgramistaAbuk/abrix?style=for-the-badge&labelColor=101418&color=9ccbfb)
![GitHub repo size](https://img.shields.io/github/repo-size/ProgramistaAbuk/abrix?style=for-the-badge&labelColor=101418&color=d3bfe6)

</div>

Mini script I made in 2 days used mainly take .war files from projects, compile them using mvn, and put them into local tomcat to test.
Program is also capable of downloading and preparing a new tomcat folder. Program hashes folder to check weather changes occured.

### TODOOOOOOOOOOOOOO
- Line `474` | add actual download of JAVA jdk (scan for all versions, let user choose, then set it up)

- Install + uninstall script
 

### parameters
`-h --help` View all params

`-a --al` Skip change detection, compile all wars

`-c --config [OPTION]`

- `gen` generate config file
- `edit` right now nothing but in future edit config from program not manually

`-sv --savechanges` Saves current changes to `abrix.dat.hash` file

`-t --tomcat [TOMCAT]` Enter directory for the tomcat you want abrix to put .war files in (only affects one run of program - to change default tomcat directory, see editing config)

`-ct --createtomcat [DIRECTORY]` Auto downloads, unzips, and sets up tomcat in specified directory, also changes config file to point to newly downloaded tomcat (to set what tomcat version you want downloaded see editing config)

`-jm --javamanual [DIRECTORY]` Forces program to use a specific directory of JAVA (keep in mind program doesn't check if the directory actually has JAVA in it)


### editing config
Config file is structured using
```commandline
[TAGNAME] {

}
```
tags.
Possible tag names are:
- `PROJECTS` For setting project directories
- `TOMCAT` To set default tomcat directory
- `PRFNA` (Project File Names), to set the .war file names that maven sets once it compiles based on `pom.xml`
- `PRFNNA` (Project File New Names), what you want abrix to set your .war files in new tomcat
- `TOMCATV` for parameter `--createtomcat`, param in this tag tells program what tomcat versison to download

#### Inside tags
Inside tags all you can do is set variables, variable names aren't checked in the program.
> [!NOTE]
> You can set variables to whatever name you may want, EXCLUDING
> ```commandline
> [TOMCAT] {
> set t = tomcatdir
> }
> ```
> This is edited when you create tomcat (using --createtomcat), as such variable name 't' cannot be changed
 
- The `PROJECTS` tag

In the projects tag, by default there are variable names pr1, pr2 (project 1, project 2).
Inside of this tag you set the project directories you want abrix to check for when running.
When setting directories always use `/` between folder names and always point to your project directory,
not  directories within your project. You may set as many projects as you want.

- The `TOMCAT` tag

In here you set your tomcat directory (top folder of tomcat directory), e.g
```commandline
[TOMCAT] {
set t = YourTomcatDirectoryHere
```
Keep in mind that for this tag you cannot change the variable name 't'.

- The `PRFNA` tag

In this tag you set the name of your compiled .wars, when using mvn clean install, it generates a war with a specific name, input that name here.
Keep in mind to put in file extension  e.g `CompileFileName.war`, you can change the compiled file name in your projects pom.xml

- The `PRFNNA` tag

Here you set the new war file names, when abrix copies the compiled mvn files to your tomcat, this is the name it will set them to.
So if you want tomcat to deploy at `/projectname`, your .war must be `projectname.war`  and that is what you set in this tag.

- The `TOMCATV` tag

The only purpose of this tag is when using param `--createtomcat`, what you input here will be the version of tomcat abrix downloads and sets up.
Keep in mind to use  the full version, e.g '10.1.3' not '10'


> [!NOTE]
> Keep in mind that when the program creates tomcat on linux, you must go into the `tomcat/bin` folder and run `sudo chmod 777 ./*sh` - this ensures all files are executable and allows tomcat to properly run

- General info on tags

All tags have the same syntax after [TAGNAME] {}, you put in variables as such:
```commandline
set varname = varvalue
```
One thing to keep in mind is whitespaces, program finds you var based on whitespaces, and thus
you must (should) only have 'set' 'space' 'varname' '=' 'varvalue' | keeping in mind none of the names can have spaces within them,
e.g varname and varvalue CANNOT have spaces between them.

Example config looks as such:
```commandline
#Main Abrix Config File
[PROJECTS] {
set pr1 = C:/__p__/--py--/abrix/test/proxyservice
set pr2 = C:/__p__/--py--/abrix/test/rating
}
[TOMCAT] {
set t = C:/debug/test67/tomcat-11
}
[PRFNA] {
set pr1 = proxyservice-2.1.war
set pr2 = rating-0.0.2-SNAPSHOT.war
}
[PRFNNA] {
set pr1 = proxyservice.war
set pr2 = ratingservice.war
}
[TOMCATV] {
set v = 11.0.13
}
```

### program files
Abrix uses only 3 files for data, logs, config and 4 files for the program itself

- Inside the `logs` folder is a `log.out` file where all logs of abrix are saved.


- `conf folder`

In the conf folder there are two files:
- `abrix.conf`
Where you put your configuration (this is where you would put what was said above)
- `abrix.dat.hash`
Program data file - DO NOT EDIT. This is where abrix stores hashes to later compare and see if project has any new changes.


### more
- Program assumes there is maven installed and in PATH, and that maven/bin has a mvn.cmd file.
To download maven click [`here`](https://maven.apache.org/download.cgi)
- Program will automatically detect if TOMCAT fails because of improper setting of JAVA_HOME and will ask user to choose JAVA version (program scans
for all JDK's on system), once user chooses, abrix will either (depending on user input), put in the env var in the startup file for tomcat,
or just do a single startup with that JAVA_HOME env
- If you get to page where program asks if install JAVA manually, that feature doesn't exist yet,
if someone would like to add it go to `main.py` line `474`



