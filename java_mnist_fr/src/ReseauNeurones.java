import java.io.FileWriter;
import java.io.BufferedWriter;

import java.io.FileReader;
import java.io.BufferedReader;


public class ReseauNeurones
{
	private static final float recogSeuil = 0.5f;

	private boolean aAppris = false;
	private int tailleQuestions;
	private int nombreNeurones;        // i.e taille des réponses
	private Activation activation;     // fonction d'activation

	private float poids[][] = {};      // nombreNeurones x tailleQuestions
	private float biais[][] = {};      // 1 x nombreNeurones
	private float somme[] = {};        // 1 x nombreNeurones
	private float reponse[] = {};      // 1 x nombreNeurones


	public ReseauNeurones(int tailleQuestions, int nombreNeurones, Activation activation)
	{
		this.tailleQuestions = tailleQuestions;
		this.nombreNeurones = nombreNeurones;
		this.activation = activation;

		float borne = 1f / (float) Math.sqrt(tailleQuestions); // pour une initialisation efficace.

		// Valeurs uniformément dans [-borne, +borne].
		this.poids = Matrice.random(nombreNeurones, tailleQuestions, -borne, borne);
		this.biais = new float[1][nombreNeurones]; // laissés nuls initialement.
		this.somme = new float[nombreNeurones];
		this.reponse = new float[nombreNeurones];
	}

	public boolean aAppris()
	{
		return this.aAppris;
	}

	public int tailleQuestions()
	{
		return this.tailleQuestions;
	}

	public int nombreNeurones()
	{
		return this.nombreNeurones;
	}

	public Activation activation()
	{
		return this.activation;
	}


	public void affiche()
	{
		System.out.println("Ce réseau de neurones a pour caractéristiques:\n");
		System.out.printf("A appris: %s\nTaille des questions: %d\nNombre de neurones: %d\nFonction d'activation: %s\n\n",
			this.aAppris ? "oui" : "non", this.tailleQuestions, this.nombreNeurones, this.activation.toString());

		System.out.print("Poids - ");
		Matrice.affiche(this.poids);

		System.out.print("Biais - ");
		Matrice.affiche(this.biais);
	}


	// Enregistre le réseau de neurones, s'il a appris.
	public void sauvegarde(String cheminDossier)
	{
		if (this.aAppris == false)
		{
			System.out.println("Ce réseau n'a rien appris, annulation de la sauvegarde.\n");
			return;
		}

		Sauvegarde.creeDossier(cheminDossier);

		try
		{
			FileWriter writer = new FileWriter(cheminDossier + "/parametres.txt");
			BufferedWriter bufferedWriter = new BufferedWriter(writer); // optimisation.

			bufferedWriter.write(Integer.toString(this.tailleQuestions));
			bufferedWriter.newLine();

			bufferedWriter.write(Integer.toString(this.nombreNeurones));
			bufferedWriter.newLine();

			bufferedWriter.write(this.activation.toString());
			bufferedWriter.newLine();

			bufferedWriter.close();
			writer.close();
		}

		catch (Exception e)
		{
			System.out.println("Impossible d'écrire dans '" + cheminDossier + "/parametres.txt'.\n");
			throw new RuntimeException();
		}

		Sauvegarde.ecrisMatrice(this.poids, cheminDossier + "/poids.bin");
		Sauvegarde.ecrisMatrice(this.biais, cheminDossier + "/biais.bin");

		System.out.printf("\nSauvegarde du réseau dans '%s' réussie.\n\n", cheminDossier);
	}


	// Charge en mémoire le réseau de neurones:
	public static ReseauNeurones charge(String cheminDossier)
	{
		int tailleQuestions, nombreNeurones;
		Activation activation;

		try
		{
			FileReader reader = new FileReader(cheminDossier + "/parametres.txt");
			BufferedReader bufferedReader = new BufferedReader(reader); // optimisation.

			tailleQuestions = Integer.parseInt(bufferedReader.readLine());
			nombreNeurones = Integer.parseInt(bufferedReader.readLine());
			activation = Activation.getActivation(bufferedReader.readLine());

			bufferedReader.close();
			reader.close();
		}

		catch (Exception e)
		{
			System.out.println("Fichier '" + cheminDossier + "/param.txt' non trouvé.\n");
			throw new RuntimeException();
		}

		ReseauNeurones reseau = new ReseauNeurones(tailleQuestions, nombreNeurones, activation);

		Sauvegarde.lisMatrice(reseau.poids, cheminDossier + "/poids.bin");
		Sauvegarde.lisMatrice(reseau.biais, cheminDossier + "/biais.bin");

		reseau.aAppris = true; // n'aurais pas été sauvegardé sans apprentissage.

		System.out.printf("\nChargement depuis '%s' réussi.\n\n", cheminDossier);

		return reseau;
	}


	// Utile en amont d'un apprentissage, d'une validation ou d'une prediction:
	private void verification(Entrees entrees)
	{
		if (entrees == null)
		{
			System.out.println("Entrees null.");
			throw new RuntimeException();
		}

		if (this.tailleQuestions != entrees.tailleQuestions())
		{
			System.out.printf("Tailles incompatibles de questions: %d vs %d.\n\n",
				this.tailleQuestions, entrees.tailleQuestions());
			throw new RuntimeException();
		}

		if (this.nombreNeurones != entrees.tailleReponses())
		{
			System.out.printf("Tailles incompatibles de reponses: %d vs %d.\n\n",
				this.nombreNeurones, entrees.tailleReponses());
			throw new RuntimeException();
		}
	}


	// Phase d'apprentissage des entrées données, par descente de gradient stochastique:
	public void apprends(Apprentissage apprentissage, Entrees entrees)
	{
		long debut = System.nanoTime();

		System.out.println("Apprentissage:");

		verification(entrees);

		for (int epoque = 0; epoque < apprentissage.nombreEpoques; ++epoque)
		{
			int somme = 0;

			for (int entree_index = 0; entree_index < entrees.nombreEntrees(); ++entree_index)
			{
				float[] question = entrees.questions[entree_index];
				float[] bonne_reponse = entrees.reponses[entree_index];

				propagation(question);

				if (apprentissage.afficheEstimations && comparaison(bonne_reponse, this.reponse))
					++somme;

				actualise(apprentissage, question, bonne_reponse);
			}

			if (apprentissage.afficheEstimations)
			{
				float estimation = 100f * somme / entrees.nombreEntrees();
				System.out.printf("\nEpoque °%d, estimation d'apprentissage: %.2f %%\n", epoque + 1, estimation);
			}

			apprentissage.vitesseApprentissage *= apprentissage.vitesseMultiplicateur;
		}

		this.aAppris = true;

		double duree = (double) (System.nanoTime() - debut) / 1000000000;

		System.out.printf("\nApprentissage terminé (%.3f s).\n", duree);
	}


	// Affichage du niveau de reconnaissance des entrées données:
	public void validation(Entrees entrees)
	{
		verification(entrees);

		if (this.aAppris == false)
		{
			System.out.println("Inutile de valider: le réseau n'a pas encore appris.");
			return;
		}

		int somme = 0;

		for (int entree_index = 0; entree_index < entrees.nombreEntrees(); ++entree_index)
		{
			float[] question = entrees.questions[entree_index];
			float[] bonne_reponse = entrees.reponses[entree_index];

			propagation(question);

			if (comparaison(bonne_reponse, this.reponse))
				++somme;
		}

		float niveau_reconnaissance = 100f * somme / entrees.nombreEntrees();

		System.out.printf("\n-> Niveau de reconnaissance: %.2f %%\n\n", niveau_reconnaissance);
	}


	// Prediction des réponses pour les entrées données. Seules les probabilités sont sauvegardées,
	// la classe prédite est obtennue en appelant: maxValeurIndex(reponse).
	public void prediction(Entrees entrees)
	{
		verification(entrees);

		if (this.aAppris == false)
		{
			System.out.println("Inutile de prédire: le réseau n'a pas encore appris.");
			return;
		}

		for (int entree_index = 0; entree_index < entrees.nombreEntrees(); ++entree_index)
		{
			float[] question = entrees.questions[entree_index];

			propagation(question);

			// Recopiage des probabilités:
			for (int i = 0; i < this.nombreNeurones; ++i)
				entrees.reponses[entree_index][i] = this.reponse[i];
		}

		System.out.println("\nPrediction terminée.\n");
	}


	// Fait produire au réseau de neurones une réponse à la question données.
	// Calculs: somme = biais + question * transposee(poids)
	// et reponse = activation(somme)
	private void propagation(float[] question)
	{
		for (int i = 0; i < this.nombreNeurones; ++i)
		{
			this.somme[i] = this.biais[0][i];

			for (int j = 0; j < this.tailleQuestions; ++j)
				this.somme[i] += this.poids[i][j] * question[j];
		}

		// Activation:
		for (int i = 0; i < this.nombreNeurones; ++i)
			this.reponse[i] = this.activation.eval(this.somme[i]);
	}


	// Modification du réseau afin d'apprendre la bonne réponse, pour la fonction de coût quadratique.
	// Calculs: temp := vitesse * gradient(activation)(somme) ° (reponse - bonne_reponse), où ° désigne
	// le produit d'Hadamard. Enfin biais -= temp et poids -= transposee(temp) * question.
	private void actualise(Apprentissage apprentissage, float[] question, float[] bonne_reponse)
	{
		for (int i = 0; i < this.nombreNeurones; ++i)
		{
			float temp = apprentissage.vitesseApprentissage * (this.reponse[i] - bonne_reponse[i]) *
				this.activation.derive_eval(this.somme[i]);

			this.biais[0][i] -= temp;

			for (int j = 0; j < this.tailleQuestions; ++j)
				this.poids[i][j] -= temp * question[j];
		}
	}


	// Renvoi l'index de la plus grande valeur du tableau:
	public static int maxValeurIndex(float[] tableau)
	{
		int index = 0;
		float max = tableau[0];

		for (int i = 1; i < tableau.length; ++i)
		{
			if (tableau[i] > max)
			{
				max = tableau[i];
				index = i;
			}
		}

		return index;
	}


	private static boolean comparaison(float[] bonne_reponse, float[] reponse)
	{
		int index_max = maxValeurIndex(reponse);

		return Math.abs(bonne_reponse[index_max] - reponse[index_max]) < recogSeuil;
	}


	public static void main(String[] args)
	{
		String dossierSauvegarde = "../sauvegardes";
		String cheminReseau = dossierSauvegarde + "/test_reseau";

		// Porte logique ET:

		float[][] questions = { {0, 0}, {0, 1}, {1, 0}, {1, 1} };
		float[][] reponses = { {0}, {0}, {0}, {1} };

		Entrees a_apprendre = new Entrees(questions, reponses);

		// Paramètres d'apprentissage:

		int nombreEpoques = 25;
		float vitesseApprentissage = 1f;
		float vitesseMultiplicateur = 1f;

		Activation activation = Activation.Sigmoide;

		// Apprentissage:

		Apprentissage apprentissage = new Apprentissage(true, nombreEpoques, vitesseApprentissage, vitesseMultiplicateur);

		ReseauNeurones reseau = new ReseauNeurones(a_apprendre.tailleQuestions(), a_apprendre.tailleReponses(), activation);

		reseau.apprends(apprentissage, a_apprendre);

		// Sauvegarde et chargement du réseau:

		reseau.sauvegarde(cheminReseau);

		ReseauNeurones reseau_lu = charge(cheminReseau);

		// Prediction:

		Entrees a_predire = new Entrees(questions, 1);

		reseau_lu.affiche();
		reseau_lu.validation(a_apprendre);
		reseau_lu.prediction(a_predire);

		a_predire.affiche();
	}
}
