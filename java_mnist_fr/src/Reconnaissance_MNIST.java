public class Reconnaissance_MNIST
{
	public static void main(String[] args)
	{
		String dossierSauvegarde = "../sauvegardes";
		String cheminReseau = dossierSauvegarde + "/reseau_MNIST";

		// Caractères à apprendre:

		Entrees a_apprendre = Pilote_MNIST.MNIST_apprentissage();

		// Paramètres d'apprentissage:

		int nombreEpoques = 10;
		float vitesseApprentissage = 0.2f;
		float vitesseMultiplicateur = 0.7f;

		Activation activation = Activation.Sigmoide;

		// Apprentissage:

		Apprentissage apprentissage = new Apprentissage(true, nombreEpoques, vitesseApprentissage, vitesseMultiplicateur);

		ReseauNeurones reseau = new ReseauNeurones(a_apprendre.tailleQuestions(), a_apprendre.tailleReponses(), activation);

		reseau.apprends(apprentissage, a_apprendre);

		// Sauvegarde et chargement du réseau:

		reseau.sauvegarde(cheminReseau);

		ReseauNeurones reseau_lu = ReseauNeurones.charge(cheminReseau);

		// Validation:

		Entrees a_reconnaitre = Pilote_MNIST.MNIST_validation();

		System.out.println("Validation de l'apprentissage:");
		reseau_lu.validation(a_apprendre);
		System.out.println("Validation de la reconnaissance:");
		reseau_lu.validation(a_reconnaitre);
	}
}
