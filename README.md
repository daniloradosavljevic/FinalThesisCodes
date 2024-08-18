# FinalThesisCodes

The complete set of source codes used for the implementation of the practical part of the final thesis "Security of Distributed Networks and Applications" at the Faculty of Engineering Sciences, University of Kragujevac.

## Distributed Networks Security source codes

Source code for the simulation of attacks on distributed network is available at **mininet-network-simulation-codes** folder of this repository, featuring **mininet_app.py** script. In order to install the required dependencies on **Linux**, it is recommended to use **instalacija.sh** bash script. 

**mininet_app.py** script features implementation of an distributed network that can be visualized with [SDN Narmox Spear](http://demo.spear.narmox.com/app/?apiurl=demo#!/mininet) like this:

![topologijademo](https://github.com/user-attachments/assets/14ea7260-29a7-4aec-930f-4d0086fb51a0)

The script also features simulation of **DDOS**, **Sybil** and **Routing** attacks. The script can be run with simple **python3 mininet_app.py** command.

## Distributed Applications Security source codes

Source codes for the simulation of attacks on distributed applications are available at **flask-hardhat-application-codes** folder of this repository, featuring **flask_app.py** script as the main executable file. In order to install the required dependencies on **Linux**, it is recommended to use **web3instalacija.sh** bash script. 

Alongside the main executable file, there is also a folder named **templates** that features all the **.html** pages of the distributed application, as well as deploy.js script that should be put in the hardhat project **/scripts** folder and **SimpleStorage.sol** in the **/contracts** folder of the same project.

The attack simulation includes **XSS**, **CSRF** and **SQL Injection** attacks, and is implemented in the script.js file.

Homepage of this distributed blockchain web3 application is shown below.
![image](https://github.com/user-attachments/assets/dc0856c3-69e2-48ba-9b3c-713fcf3746df)

The application can be run with **npx hardhat node;
npx hardhat run scripts/deploy.js --network localhost;
python3 flask_app.py** commands in the respective folders of the project.


