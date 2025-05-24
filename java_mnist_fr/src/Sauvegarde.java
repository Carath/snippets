import java.io.File;

import java.io.FileOutputStream;
import java.io.BufferedOutputStream;
import java.io.DataOutputStream;

import java.io.FileInputStream;
import java.io.BufferedInputStream;
import java.io.DataInputStream;


public class Sauvegarde
{
	// Crée un dossier, ne fait rien s'il existe déjà.
	public static void creeDossier(String cheminDossier)
	{
		File dossier = new File(cheminDossier);
		dossier.mkdirs();
	}

	public static long poidsFichier(String cheminFicher) // in bytes!
	{
		File fichier = new File(cheminFicher);
		long poids = fichier.length();
		return poids;
	}

	// Renvoi le nombre de floats présents dans le fichier.
	public static long nombreDeFloats(String cheminFicher)
	{
		return poidsFichier(cheminFicher) / Float.BYTES;
	}

	// Ecrit la matrice de floats dans un fichier binaire, écrase le fichier s'il existe déjà.
	public static void ecrisMatrice(float[][] matrice, String cheminFicher)
	{
		try
		{
			FileOutputStream fos = new FileOutputStream(cheminFicher);
			BufferedOutputStream bos = new BufferedOutputStream(fos); // optimisation.
			DataOutputStream dos = new DataOutputStream(bos);

			for (int i = 0; i < Matrice.lignes(matrice); ++i)
			{
				for (int j = 0; j < Matrice.colonnes(matrice); ++j)
					dos.writeFloat(matrice[i][j]);
			}

			dos.close();
			bos.close();
			fos.close();

			// System.out.println(cheminFicher + " -> écriture réussie.\n");
		}

		catch (Exception e)
		{
			System.out.println("Impossible d'écrire dans '" + cheminFicher + "'.\n");
			throw new RuntimeException();
		}
	}

	// Lit une matrice de floats depuis un fichier binaire. La matrice doit être déjà créée.
	public static void lisMatrice(float[][] matrice, String cheminFicher)
	{
		int lignes = Matrice.lignes(matrice);
		int colonnes = Matrice.colonnes(matrice);

		try
		{
			FileInputStream fis = new FileInputStream(cheminFicher);
			BufferedInputStream bis = new BufferedInputStream(fis); // optimisation.
			DataInputStream dis = new DataInputStream(bis);

			if (nombreDeFloats(cheminFicher) < lignes * colonnes)
			{
				System.out.println("Le fichier '" + cheminFicher + "' ne contient pas assez de nombres...\n");
				throw new RuntimeException();
			}

			long nombre_cases = lignes * colonnes;

			for (int i = 0; i < nombre_cases; ++i)
				matrice[i / colonnes][i % colonnes] = dis.readFloat();

			dis.close();
			bis.close();
			fis.close();

			// System.out.println(cheminFicher + " -> lecture réussie.\n");
		}

		catch (Exception e)
		{
			System.out.println("Fichier '" + cheminFicher + "' non trouvé.\n");
			throw new RuntimeException();
		}
	}

	public static void main(String[] args)
	{
		String nomDossier = "../sauvegardes";
		String cheminFicher = nomDossier + "/test_matrice_fichier.bin";
		creeDossier(nomDossier);

		float[][] mat = { {1, 2, 3}, {4, 5, 6} };

		ecrisMatrice(mat, cheminFicher);

		float[][] matrice_lue = new float[Matrice.lignes(mat)][Matrice.colonnes(mat)];

		lisMatrice(matrice_lue, cheminFicher);

		Matrice.affiche(matrice_lue);

		System.out.println("\nNombre de floats: " + nombreDeFloats(cheminFicher));
	}
}
