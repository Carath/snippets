// https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/util/HashMap.html
import java.util.*;

public class Test
{
	public static void main(String[] args)
	{
		HashMap<Integer, String> map = new HashMap<Integer, String>();

		// Inserting (key, values) pairs in the HashMap:
		map.put(10, "Geeks");
		map.put(20, "Geeks");
		map.put(25, "Welcomes");
		map.put(20, "All"); // overwriting an existing key.
		map.remove(25);

		// Keys presence test:
		System.out.printf("Key %d exist: %b\n", 42, map.containsKey(42)); // better
		// System.out.printf("Key %d exist: %b\n", 20, map.get(20) != null);

		// Easy printing of the whole map:
		System.out.println("\nHash map: " + map + "\nSize: " + map.size());
		System.out.println("\nIs empty: " + map.isEmpty() + "\n");

		// Iterating and displaying the HashMap:
		for (Integer key : map.keySet()) {
			String value = map.get(key);
			System.out.printf("%d -> %s\n", key, value);
		}
		System.out.println("");

		// Other variant:
		for (Map.Entry<Integer, String> entry : map.entrySet()) {
			Integer key = entry.getKey();
			String value = entry.getValue();
			System.out.printf("%d -> %s\n", key, value);
		}
		System.out.println("");
	}
}
