// Pilote pour lire la base de donnée MNIST - reconnaissance de caractères:
// http://yann.lecun.com/exdb/mnist/

import java.io.File;

import java.io.FileInputStream;
import java.io.BufferedInputStream;
import java.io.DataInputStream;


public class Pilote_MNIST
{
	public static final String dossier_MNIST = "../mnist_samples";

	private static final int tailleReponses = 10; // entiers de 0 à 9.
	private static final int dimensionImage = 28; // images de 28 x 28 pixels.
	private static final float epsilon = 0.00001f;


	public static Entrees MNIST_apprentissage()
	{
		System.out.println("Chargement des entrees à apprendre de la base MNIST:");
		String chemin_images = dossier_MNIST + "/train-images-idx3-ubyte";
		String chemin_labels = dossier_MNIST + "/train-labels-idx1-ubyte";

		float[][] questions = MNIST_loadImages(chemin_images);
		float[][] reponses = MNIST_loadLabels(chemin_labels);

		Entrees entrees = new Entrees(questions, reponses);

		System.out.println("Chargement réussi.\n");

		return entrees;
	}


	public static Entrees MNIST_validation()
	{
		System.out.println("Chargement des entrees à reconnaître de la base MNIST:");
		String chemin_images = dossier_MNIST + "/t10k-images-idx3-ubyte";
		String chemin_labels = dossier_MNIST + "/t10k-labels-idx1-ubyte";

		float[][] questions = MNIST_loadImages(chemin_images);
		float[][] reponses = MNIST_loadLabels(chemin_labels);

		Entrees entrees = new Entrees(questions, reponses);

		System.out.println("Chargement réussi.\n");

		return entrees;
	}


	private static float[][] MNIST_loadImages(String cheminFicher)
	{
		try
		{
			FileInputStream fis = new FileInputStream(cheminFicher);
			BufferedInputStream bis = new BufferedInputStream(fis); // optimisation.
			DataInputStream dis = new DataInputStream(bis);

			int nombre_magique = dis.readInt();
			int nombre_images = dis.readInt(); // 60000 pour l'apprentissage, 10000 pour la validation.
			int lignes = dis.readInt(); // 28
			int colonnes = dis.readInt(); // 28
			int nombre_pixels = lignes * colonnes; // 784

			if (nombre_magique != 2051)
			{
				System.out.printf("\nNombre magique %d incorrect dans la lecture de '%s'.\n\n",
					nombre_magique, cheminFicher);
				throw new RuntimeException();
			}

			// 'nombre_images' images de taille 28 x 28, en niveux de gris: [0, 255].
			float[][] images = new float[nombre_images][nombre_pixels];

			for (int image_index = 0; image_index < nombre_images; ++image_index)
			{
				for (int pixel = 0; pixel < nombre_pixels; ++pixel)
				{
					int nivreau_de_gris = dis.readByte() & 0xFF; // ramené dans [0, 255].

					images[image_index][pixel] = (float) nivreau_de_gris / 255; // ramené dans [0, 1].
				}
			}

			dis.close();
			bis.close();
			fis.close();

			// System.out.println(cheminFicher + " -> lecture réussie.\n");

			return images;
		}

		catch (Exception e)
		{
			System.out.println("Fichier '" + cheminFicher + "' non trouvé.\n");
			throw new RuntimeException();
		}
	}


	private static float[][] MNIST_loadLabels(String cheminFicher)
	{
		try
		{
			FileInputStream fis = new FileInputStream(cheminFicher);
			BufferedInputStream bis = new BufferedInputStream(fis); // optimisation.
			DataInputStream dis = new DataInputStream(bis);

			int nombre_magique = dis.readInt();
			int nombre_labels = dis.readInt(); // 60000 pour l'apprentissage, 10000 pour la validation.

			if (nombre_magique != 2049)
			{
				System.out.printf("\nNombre magique %d incorrect dans la lecture de '%s'.\n\n",
					nombre_magique, cheminFicher);
				throw new RuntimeException();
			}

			// 'nombre_labels' labels, de 0 à 9.
			float[][] labels = new float[nombre_labels][tailleReponses];

			for (int label_index = 0; label_index < nombre_labels; ++label_index)
			{
				int label = dis.readByte(); // entier entre 0 et 9.

				labels[label_index][label] = 1f;
			}

			dis.close();
			bis.close();
			fis.close();

			// System.out.println(cheminFicher + " -> lecture réussie.\n");

			return labels;
		}

		catch (Exception e)
		{
			System.out.println("Fichier '" + cheminFicher + "' non trouvé.\n");
			throw new RuntimeException();
		}
	}


	public static void afficheImageNiveauxDeGris(float[] image, int largeur, int hauteur)
	{
		if (image == null)
		{
			System.out.println("\nImpossible d'afficher dans la console une image null.\n");
			throw new RuntimeException();
		}

		if (image.length < largeur * hauteur)
		{
			System.out.printf("\nL'image donnée est trop petit pour être affichée comme souhaité (%d vs %d pixels).\n",
				image.length, largeur * hauteur);
			throw new RuntimeException();
		}

		for (int ligne = 0; ligne < hauteur; ++ligne)
		{
			for (int colonne = 0; colonne < largeur; ++colonne)
			{
				int position = ligne * largeur + colonne;

				if (image[position] > epsilon)
					System.out.printf("%5.1f", image[position]);
				else
					System.out.printf("     ");
			}

			System.out.println();
		}

		System.out.println();
	}


	// Affiche dans la console les 'n' premières images de la base MNIST considérée:
	public static void affiche_MNIST(Entrees entrees_MNIST, int n)
	{
		for (int i = 0; i < n; ++i)
			afficheImageNiveauxDeGris(entrees_MNIST.questions[i], dimensionImage, dimensionImage);
	}


	public static void main(String[] args)
	{
		Entrees a_apprendre = MNIST_apprentissage();
		affiche_MNIST(a_apprendre, 5);

		Entrees a_reconnaitre = MNIST_validation();
		affiche_MNIST(a_reconnaitre, 5);
	}
}
