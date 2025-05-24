public class Apprentissage
{
	public boolean afficheEstimations;
	public int nombreEpoques;
	public float vitesseApprentissage;
	public float vitesseMultiplicateur;


	public Apprentissage(boolean afficheEstimations, int nombreEpoques, float vitesseApprentissage, float vitesseMultiplicateur)
	{
		this.afficheEstimations = afficheEstimations;
		this.nombreEpoques = nombreEpoques;
		this.vitesseApprentissage = vitesseApprentissage;
		this.vitesseMultiplicateur = vitesseMultiplicateur;
	}
}
