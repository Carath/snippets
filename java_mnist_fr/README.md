# MNIST java

*Reconnaissance de caractères écrits à la main à l'aide d'un réseau de neurones monocouche.*

Archive d'un projet datant de 2021.


## Installation

Installer le package Linux suivant:

```sh
sudo apt-get install openjdk-17-jdk
```

Puis télécharger la base de données MNIST à partir du site [officiel](https://yann.lecun.org/exdb/mnist/index.html).

Cette base de données contient 4 fichiers binaires compressés, pesant au total 52 MB une fois décompressés:

- ``` t10k-images-idx3-ubyte ```
- ``` t10k-labels-idx1-ubyte ```
- ``` train-images-idx3-ubyte ```
- ``` train-labels-idx1-ubyte ```


## Utilisation

Pour compiler le projet et lancer l'apprentissage de la base de données précédemment citée, se placer
depuis un terminal dans le dossier ``` src/ ```, puis exécuter les commandes:

```sh
javac *.java
java Reconnaissance_MNIST
```
