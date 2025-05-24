public class Matrice
{
	public static int lignes(float[][] mat)
	{
		return mat.length;
	}

	public static int colonnes(float[][] mat)
	{
		return mat[0].length;
	}

	public static void affiche(float[][] mat)
	{
		System.out.printf("Matrice %d x %d:\n\n", lignes(mat), colonnes(mat));

		for (int i = 0; i < lignes(mat); ++i)
		{
			for (int j = 0; j < colonnes(mat); ++j)
				System.out.printf("%10.2f", mat[i][j]);
			System.out.println();
		}

		System.out.println();
	}

	// Renvoi une matrice dont les valeurs sont tirées uniformément dans entre min et max.
	public static float[][] random(int lignes, int colonnes, float min, float max)
	{
		float[][] mat = new float[lignes][colonnes];

		for (int i = 0; i < lignes; ++i)
		{
			for (int j = 0; j < colonnes; ++j)
				mat[i][j] = (max - min) * (float) Math.random() + min;
		}

		return mat;
	}

	public static float[][] copie(float[][] mat)
	{
		float[][] mat2 = new float[lignes(mat)][colonnes(mat)];

		for (int i = 0; i < lignes(mat); ++i)
		{
			for (int j = 0; j < colonnes(mat); ++j)
				mat2[i][j] = mat[i][j];

		}

		return mat2;
	}

	public static void main(String[] args)
	{
		float[][] matrice = random(3, 4, -1f, 1f);

		affiche(matrice);
	}
}
