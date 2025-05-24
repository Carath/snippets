public enum Activation
{
	Seuil,
	ReLu,
	Sigmoide,
	Tanh;

	public float eval(float x)
	{
		if (this == Seuil)
			return x < 0 ? 0f : 1f;

		else if (this == ReLu)
			return x < 0 ? 0f : x;

		else if (this == Sigmoide)
			return 1f / (1f + (float) Math.exp(-x));

		else if (this == Tanh)
			return (float) Math.tanh(x);

		else
		{
			System.out.println("\nFonction d'activation invalide.\n");
			throw new RuntimeException();
		}
	}

	public float derive_eval(float x)
	{
		if (this == Seuil)
			return 1f; // pour ne pas être 0...

		else if (this == ReLu)
			return x < 0 ? 0f : 1f;

		else if (this == Sigmoide)
		{
			float y = this.eval(x);
			return y * (1 - y);
		}

		else if (this == Tanh)
		{
			float y = this.eval(x);
			return 1 - y * y;
		}

		else
		{
			System.out.println("\nFonction d'activation invalide.\n");
			throw new RuntimeException();
		}
	}

	// Renvoi une activation à partir de sa string:
	public static Activation getActivation(String nom)
	{
		if (nom.equals(Seuil.toString()))
			return Seuil;

		else if (nom.equals(ReLu.toString()))
			return ReLu;

		else if (nom.equals(Sigmoide.toString()))
			return Sigmoide;

		else if (nom.equals(Tanh.toString()))
			return Tanh;

		else
		{
			System.out.println("\nFonction d'activation invalide.\n");
			throw new RuntimeException();
		}
	}

	public static void main(String[] args)
	{
		System.out.println(Seuil.toString());

		Activation act = getActivation("Tanh");

		System.out.println(act.toString());

		System.out.printf("%.3f\n", Sigmoide.eval(1));
	}
}
