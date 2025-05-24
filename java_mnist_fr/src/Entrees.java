public class Entrees
{
	private int nombreEntrees;
	private int tailleQuestions;
	private int tailleReponses;

	public float[][] questions = {}; // nombreEntrees x tailleQuestions
	public float[][] reponses = {};  // nombreEntrees x tailleReponses


	// Constructeur pour l'apprentissage:
	public Entrees(float[][] questions, float[][] reponses)
	{
		if (questions == null || reponses == null)
		{
			System.out.println("questions ou reponses: null");
			throw new RuntimeException();
		}

		if (Matrice.lignes(questions) != Matrice.lignes(reponses))
		{
			System.out.printf("\nNombre d'entrées incompatible: %d vs %d.\n\n",
				Matrice.lignes(questions), Matrice.lignes(reponses));
			throw new RuntimeException();
		}

		this.nombreEntrees = Matrice.lignes(questions);
		this.tailleQuestions = Matrice.colonnes(questions);
		this.tailleReponses = Matrice.colonnes(reponses);
		this.questions = questions;
		this.reponses = reponses;
	}

	// Constructeur pour la reconnaissance:
	public Entrees(float[][] questions, int tailleReponses)
	{
		if (questions == null)
		{
			System.out.println("questions: null");
			throw new RuntimeException();
		}

		this.nombreEntrees = Matrice.lignes(questions);
		this.tailleQuestions = Matrice.colonnes(questions);
		this.tailleReponses = tailleReponses;
		this.questions = questions;
		this.reponses = new float[this.nombreEntrees][this.tailleReponses];
	}

	public int nombreEntrees()
	{
		return this.nombreEntrees;
	}

	public int tailleQuestions()
	{
		return this.tailleQuestions;
	}

	public int tailleReponses()
	{
		return this.tailleReponses;
	}

	public void affiche()
	{
		System.out.printf("Il y a %d entrées. Taille des questions: %d, taille des réponses: %d.\n\n",
			this.nombreEntrees, this.tailleQuestions, this.tailleReponses);

		System.out.print("Questions - ");
		Matrice.affiche(this.questions);

		System.out.print("Réponses - ");
		Matrice.affiche(this.reponses);
	}

	public static void main(String[] args)
	{
		float[][] questions = { {1, 2}, {3, 4}, {5, 6}, {7, 8} };

		Entrees entrees = new Entrees(questions, 3);

		entrees.affiche();
	}
}
